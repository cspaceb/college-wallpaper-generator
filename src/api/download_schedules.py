import os
import json
import requests
import unicodedata
from dotenv import load_dotenv

# -------------------------------------------------
# Load .env for CFBD_API_KEY
# -------------------------------------------------
load_dotenv()
API_KEY = os.getenv("CFBD_API_KEY")
if not API_KEY:
    raise Exception("CFBD_API_KEY missing from environment variables")

HEADERS = {"Authorization": f"Bearer {API_KEY}"}

# -------------------------------------------------
# Resolve save directory
# -------------------------------------------------
SCRIPT_PATH = os.path.abspath(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(SCRIPT_PATH), "..", ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "schedules")
os.makedirs(DATA_DIR, exist_ok=True)

print("Saving schedules to:", DATA_DIR)


# -------------------------------------------------
# Helpers
# -------------------------------------------------
def normalize(name: str) -> str:
    """Same normalization rules used for logos."""
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    name = (
        name.replace(" ", "_")
        .replace("&", "and")
        .replace(".", "")
        .replace("'", "")
        .replace("-", "_")
    )
    return name


def format_date(iso_str: str) -> str:
    """Convert 2025-09-02T19:00:00.000Z → 09-02"""
    date = iso_str.split("T")[0]
    _, m, d = date.split("-")
    return f"{m}-{d}"


# -------------------------------------------------
# Fetch FBS + FCS team lists
# -------------------------------------------------
def fetch_fbs_teams():
    url = "https://api.collegefootballdata.com/teams?division=fbs"
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    return {team["school"] for team in r.json()}


def fetch_fcs_teams():
    url = "https://api.collegefootballdata.com/teams?division=fcs"
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    return {team["school"] for team in r.json()}


# -------------------------------------------------
# Fetch ALL 2025 regular-season games
# -------------------------------------------------
def fetch_all_games():
    url = "https://api.collegefootballdata.com/games?year=2025&seasonType=regular"
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    games = r.json()
    print("Total games:", len(games))
    return games


# -------------------------------------------------
# Build schedules for BOTH FBS + FCS
# -------------------------------------------------
def main():
    print("\nFetching FBS teams...")
    fbs_teams = fetch_fbs_teams()
    print("FBS teams:", len(fbs_teams))

    print("\nFetching FCS teams...")
    fcs_teams = fetch_fcs_teams()
    print("FCS teams:", len(fcs_teams))

    # ALL TEAMS INCLUDED
    all_teams = fbs_teams | fcs_teams
    print("\nTotal teams with schedules:", len(all_teams))

    # Prepare dictionary
    schedules = {team: [] for team in all_teams}

    print("\nFetching all games...")
    games = fetch_all_games()

    print("\nProcessing games...")

    for game in games:

        # Required fields
        if not all(k in game for k in ("homeTeam", "awayTeam", "startDate")):
            continue

        home = game["homeTeam"]
        away = game["awayTeam"]
        date = format_date(game["startDate"])

        # Determine classifications
        home_cls = game.get("homeClassification")
        away_cls = game.get("awayClassification")

        # Add home schedule entry if team exists in ALL (FBS + FCS)
        if home in schedules:
            schedules[home].append({
                "opponent": away,
                "opponent_logo": f"{normalize(away)}.png",
                "date": date,
                "home": True
            })

        # Add away schedule entry if team exists in ALL
        if away in schedules:
            schedules[away].append({
                "opponent": home,
                "opponent_logo": f"{normalize(home)}.png",
                "date": date,
                "home": False
            })


    # -------------------------------------------------
    # Save schedules
    # -------------------------------------------------
    print("\nSaving files...")

    saved_count = 0

    for team, sched in schedules.items():
        if len(sched) == 0:
            continue  # Some FCS teams won't have games yet

        # Sort by date string (MM-DD)
        sched.sort(key=lambda g: g["date"])

        filepath = os.path.join(DATA_DIR, f"{normalize(team)}.json")

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(sched, f, indent=4)

        print("Saved:", filepath)
        saved_count += 1

    print("\n✔ FINISHED!")
    print("Teams with schedules saved:", saved_count)


if __name__ == "__main__":
    main()
