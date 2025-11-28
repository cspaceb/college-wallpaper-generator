from PIL import Image, ImageDraw, ImageFont
from src.generator.wallpaper_base import (
    asset_path,
    load_logo,
    load_small_logo,
    add_logo_stroke,
    hex_to_rgb,
    get_team_colors_from_logo,
    create_solid_background,
    create_gradient,
)


# ---------------------------------------------------------
# TEXT STROKE HELPER
# ---------------------------------------------------------

def draw_text_with_stroke(draw, position, text, font,
                          fill, stroke_color, stroke_width=2):
    x, y = position

    for dx in (-stroke_width, 0, stroke_width):
        for dy in (-stroke_width, 0, stroke_width):
            if dx != 0 or dy != 0:
                draw.text(
                    (x + dx, y + dy),
                    text,
                    font=font,
                    fill=stroke_color,
                    anchor="mm"
                )

    draw.text((x, y), text, font=font, fill=fill, anchor="mm")


# ---------------------------------------------------------
#  MAIN MOBILE WALLPAPER GENERATOR (ENHANCED)
# ---------------------------------------------------------

def generate_mobile_wallpaper(
    team_name,
    schedule,
    logo_path,
    user_color=None,
    gradient_enabled=False,
    style="linear",
    color1=None,
    color2=None,
    angle=0,
    noise_detail=2,
    stickerbomb=False,
    show_schedule=True,
):
    WIDTH, HEIGHT = 1284, 2778

    # ---------------------------------------------------------
    #  STICKER BOMB MODE
    # ---------------------------------------------------------
    if stickerbomb:
        bg_path = asset_path("data/stickerbomb/mobile.png")
        bg = Image.open(bg_path).convert("RGB")

        # 💥 BIG LOGO FOR MOBILE
        logo = load_logo(asset_path(logo_path), max_width=1800)
        logo = add_logo_stroke(logo, stroke_size=14)

        x = (WIDTH - logo.width) // 2
        y = (HEIGHT - logo.height) // 2
        bg.paste(logo, (x, y), logo)
        return bg

    # ---------------------------------------------------------
    #  NORMAL BACKGROUND MODE
    # ---------------------------------------------------------
    if gradient_enabled:
        c1 = hex_to_rgb(color1)
        c2 = hex_to_rgb(color2)

        if not c1 or not c2:
            primary_rgb, secondary_rgb = get_team_colors_from_logo(asset_path(logo_path))
            if not c1:
                c1 = primary_rgb
            if not c2:
                c2 = secondary_rgb

        bg = create_gradient(
            WIDTH, HEIGHT,
            style,
            c1, c2,
            angle,
            noise_detail=noise_detail
        )

    else:
        if user_color:
            c = hex_to_rgb(user_color)
        else:
            c, _ = get_team_colors_from_logo(asset_path(logo_path))

        bg = create_solid_background(WIDTH, HEIGHT, c)

    draw = ImageDraw.Draw(bg)

    # ---------------------------------------------------------
    #  HERO LOGO (BIG)
    # ---------------------------------------------------------
    hero_logo = load_logo(asset_path(logo_path), max_width=1800)
    hero_logo = add_logo_stroke(hero_logo, stroke_size=14)

    if not show_schedule:
        x = (WIDTH - hero_logo.width) // 2
        y = (HEIGHT - hero_logo.height) // 2
        bg.paste(hero_logo, (x, y), hero_logo)
        return bg

    # With schedule → place near top
    bg.paste(hero_logo, ((WIDTH - hero_logo.width) // 2, 300), hero_logo)

     # ---------------------------------------------------------
    #  SCHEDULE GRID — 4 ROWS × 3 COLUMNS
    # ---------------------------------------------------------
    items = [
        {
            "opponent": g["opponent"],
            "opponent_logo": g["opponent_logo"],
            "date": g["date"],
            "home": g["home"],
        }
        for g in schedule
        if g["opponent"] != "BYE"
    ][:12]

    ROWS, COLS = 4, 3
    GRID_START_Y = 1050
    ROW_SPACING = 230
    COLUMN_SPACING = 300
    GRID_LEFT_X = WIDTH // 2 - ((COLS - 1) * COLUMN_SPACING) // 2

    OPP_LOGO_SIZE = 150

    font_path = asset_path("src/generator/fonts/Montserrat-Bold.ttf")
    DATE_FONT = ImageFont.truetype(font_path, 40)

    idx = 0
    for r in range(ROWS):
        for c in range(COLS):
            if idx >= len(items):
                break

            item = items[idx]
            idx += 1

            cell_x = GRID_LEFT_X + c * COLUMN_SPACING
            cell_y = GRID_START_Y + r * ROW_SPACING

            opp_path = f"data/logos/{item['opponent_logo']}"
            opp_logo = load_small_logo(opp_path, max_size=OPP_LOGO_SIZE)
            opp_logo = add_logo_stroke(opp_logo, stroke_size=3)
            bg.paste(opp_logo, (cell_x - opp_logo.width // 2, cell_y), opp_logo)

            date_y = cell_y + OPP_LOGO_SIZE + 34

            draw_text_with_stroke(
                draw,
                (cell_x, date_y),
                item["date"],
                DATE_FONT,
                fill="white" if not item["home"] else "black",
                stroke_color="black" if not item["home"] else "white",
                stroke_width=2
            )

    return bg
