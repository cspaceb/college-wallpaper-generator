import os
import json
from io import BytesIO
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request

from src.generator.wallpaper_pc import generate_pc_wallpaper
from src.generator.wallpaper_mobile import generate_mobile_wallpaper

from src.generator.wallpaper_base import (
    asset_path,
    get_team_colors_from_logo,
)

app = FastAPI()

# ---------------------------------------------------------
#  STATIC + TEMPLATE SETUP
# ---------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "ui", "templates"))

app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "ui", "static")),
    name="static",
)

app.mount(
    "/data",
    StaticFiles(directory=asset_path("data")),
    name="data",
)

app.mount(
    "/dropdown",
    StaticFiles(directory=asset_path("data/logos_dropdown")),
    name="dropdown",
)


# ---------------------------------------------------------
#  HOME PAGE
# ---------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ---------------------------------------------------------
#  TEAM LIST
# ---------------------------------------------------------

@app.get("/teams")
async def get_teams():
    logos_dir = asset_path("data/logos")
    schedules_dir = asset_path("data/schedules")

    if not os.path.exists(logos_dir):
        raise HTTPException(500, "Logos folder not found")

    if not os.path.exists(schedules_dir):
        raise HTTPException(500, "Schedules folder not found")

    teams = []

    for file in os.listdir(logos_dir):
        if not file.endswith(".png"):
            continue

        team_key = file.replace(".png", "")
        schedule_file = f"{team_key}.json"

        if os.path.exists(os.path.join(schedules_dir, schedule_file)):
            name = team_key.replace("_", " ")
            teams.append({
                "name": name,
                "logo": file
            })

    teams.sort(key=lambda t: t["name"])
    return {"teams": teams}


# ---------------------------------------------------------
#  TEAM COLORS
# ---------------------------------------------------------

@app.get("/team-colors")
async def team_colors(team: str):
    filename = team.replace(" ", "_") + ".png"
    logo_path = asset_path(f"data/logos/{filename}")

    if not os.path.exists(logo_path):
        raise HTTPException(404, "Team logo not found.")

    primary_rgb, secondary_rgb = get_team_colors_from_logo(logo_path)

    def rgb_to_hex(rgb):
        return "#{:02X}{:02X}{:02X}".format(*rgb)

    return {
        "primary": rgb_to_hex(primary_rgb),
        "secondary": rgb_to_hex(secondary_rgb)
    }


# ---------------------------------------------------------
#  LOAD SCHEDULE
# ---------------------------------------------------------

def load_schedule(team_name: str):
    filename = team_name.replace(" ", "_") + ".json"
    path = asset_path(f"data/schedules/{filename}")

    if not os.path.exists(path):
        raise HTTPException(404, f"No schedule found for {team_name}")

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------
#  GENERATE WALLPAPER (TEAM + STICKERBOMB)
# ---------------------------------------------------------

@app.get("/generate")
async def generate(
    team: str = None,
    type: str = None,

    # Color mode params
    color: str = None,
    gradient_enabled: int = 0,
    style: str = "linear",
    color1: str = None,
    color2: str = None,
    angle: int = 0,
    noise_detail: int = 2,

    # Stickerbomb
    stickerbomb: int = 0,
):
    """
    Generates wallpapers for:
    ✔ Team Mode (with schedule)
    ✔ Sticker Bomb Mode (no schedule, fixed PNG backgrounds)
    """

    if type not in ("pc", "mobile"):
        raise HTTPException(400, "Invalid wallpaper type.")

    if not team:
        raise HTTPException(400, "Team is required.")

    logo_filename = team.replace(" ", "_") + ".png"
    logo_path = f"data/logos/{logo_filename}"

    # ---------------------------------------------------------
    # Sticker Bomb Mode (fixed PNG backgrounds)
    # ---------------------------------------------------------
    if int(stickerbomb) == 1:
        show_schedule = False

        if type == "pc":
            img = generate_pc_wallpaper(
                team,
                schedule=None,
                logo_path=logo_path,
                stickerbomb=True,
                show_schedule=False
            )
        else:
            img = generate_mobile_wallpaper(
                team,
                schedule=None,
                logo_path=logo_path,
                stickerbomb=True,
                show_schedule=False
            )

        img_bytes = BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        return StreamingResponse(img_bytes, media_type="image/png")

    # ---------------------------------------------------------
    # Team Mode (Normal) = schedule always ON
    # ---------------------------------------------------------

    schedule = load_schedule(team)

    kwargs = dict(
        user_color=color,
        gradient_enabled=bool(int(gradient_enabled)),
        style=style,
        color1=color1,
        color2=color2,
        angle=int(angle),
        noise_detail=int(noise_detail),
        stickerbomb=False,
        show_schedule=True,
    )

    if type == "pc":
        img = generate_pc_wallpaper(team, schedule, logo_path, **kwargs)
    else:
        img = generate_mobile_wallpaper(team, schedule, logo_path, **kwargs)

    img_bytes = BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    return StreamingResponse(img_bytes, media_type="image/png")
