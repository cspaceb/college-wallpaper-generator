import os
import json
import unicodedata
from src.api.client import CFBDClient
from src.api.teams import fetch_all_teams
from src.generator.wallpaper_base import asset_path

SCHEDULE_DIR = asset_path("data/schedules")
os.makedirs(SCHEDULE_DIR, exist_ok=True)

client = CFBDClient()


# ---------------------------------------------------------
# NORMALIZE FILENAMES (same as logos)
# ---------------------------------------------------------

def normalize_filename(name: str) -> str:
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    for ch in ["'", '"', ".", ",", "&", "(", ")"]:
        name = name.replace(ch, "")
    name = name.replace(" ", "_")
    return name


# ---------------------------------------------------------
# SIMPLIFY GAME DATA FOR WALLPAPER GENERATOR
# ---------------------------------------------------------

def simplify_game(game):
    """
    Converts CFBD game JSON into your schedule format:
    {
        "opponent": <name>,
        "opponent_logo": <filename.png>,
        "date": "MM-DD",
        "home": True/False
    }
    """

    # Determine if home or away
    home_team = game.get("home_team")
    away_team = game.get("away_team")
    date = game.get("start_date", "")[:10]  # "2024-09-14"
    date = date[5:].replace("-", "-")       # "09-14"

    # Normalize names for logo mapping
    home_file = normalize_filename(home_team) + ".png"
    away_file = normalize_filename(away_team) + ".png"

    # Determine opponent
    if game["home_team"] == game.get("team"):
        opponent = away_team
        opponent_file = away_file
        is_home = True
    else:
        opponent = home_team
        opponent_file = home_file
        is_home = False

    return {
        "opponent": opponent,
        "opponent_logo": opponent_file,
        "date": date,
        "home": is_home
    }


# ---------------------------------------------------------
# FETCH SCHEDULE FOR A SINGLE TEAM
# ---------------------------------------------------------

def fetch_team_schedule(team, year=2024):
    params = {
        "team": team,
        "year": year
    }

    games = client.get("/games", params=params)

    simplified = []
    for g in games:
        g["team"] = team  # tag so we know which side of the matchup this is
        simplified.append(simplify_game(g))

    # Save with consistent filename
    file_name = normalize_filename(team) + ".json"
    save_path = os.path.join(SCHEDULE_DIR, file_name)

    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(simplified, f, indent=2)

    print(f"[OK] Saved: {file_name}")
    return simplified


# ---------------------------------------------------------
# DOWNLOAD ALL FBS + FCS SCHEDULES
# ---------------------------------------------------------

def fetch_all_schedules(year=2024):
    teams = fetch_all_teams()
    print(f"Found {len(teams)} teams (FBS + FCS)")

    for team in teams:
        name = team["school"]
        try:
            fetch_team_schedule(name, year)
        except Exception as e:
            print(f"[ERROR] {name}: {e}")
