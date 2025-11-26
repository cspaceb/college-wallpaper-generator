# --- File: src/generator/sticker_bomb.py
import os
import random
from PIL import Image
from src.generator.wallpaper_base import asset_path, ensure_output_dir, load_small_logo

# Solid charcoal background
BG_COLOR = (17, 17, 17)

SIZES = {
    "pc": (2560, 1440),
    "mobile": (1284, 2778),
}

# SEC teams — filenames will be matched after replacing spaces with underscores
SEC_TEAMS = {
    "Alabama", "Auburn", "Arkansas", "Florida", "Georgia", "Kentucky",
    "LSU", "Mississippi_State", "Missouri", "Ole_Miss",
    "Oklahoma", "South_Carolina", "Tennessee", "Texas", "Texas_A&M", "Vanderbilt"
}

def get_all_logos():
    logos_dir = asset_path("data/logos")
    return [
        os.path.join(logos_dir, f)
        for f in os.listdir(logos_dir)
        if f.lower().endswith(".png") and f != "fallback.png"
    ]

def split_sec_and_others(logos):
    """Split logo paths into SEC and non-SEC based on filename."""
    sec = []
    others = []

    for path in logos:
        filename = os.path.basename(path).replace(".png", "")
        if filename in SEC_TEAMS:
            sec.append(path)
        else:
            others.append(path)

    return sec, others

def paste_random_logo(canvas, logo_path, WIDTH, HEIGHT):
    """Helper to paste a logo multiple times with random size/rotation."""
    for _ in range(random.randint(5, 8)):
        try:
            size = random.randint(70, 180)
            logo = load_small_logo(logo_path, max_size=size)
            logo = logo.rotate(random.randint(-25, 25), expand=True)

            x = random.randint(0, WIDTH - logo.width)
            y = random.randint(0, HEIGHT - logo.height)

            canvas.paste(logo, (x, y), logo)
        except Exception:
            continue

def generate_sticker_bomb(conferences, wallpaper_type):
    if wallpaper_type not in SIZES:
        raise ValueError("Invalid type. Use 'pc' or 'mobile'.")

    WIDTH, HEIGHT = SIZES[wallpaper_type]
    canvas = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)

    logos = get_all_logos()
    if not logos:
        raise ValueError("No logos found.")

    # NEW: Split into SEC on top
    sec_logos, other_logos = split_sec_and_others(logos)

    # Shuffle inside each group for randomness
    random.shuffle(other_logos)
    random.shuffle(sec_logos)

    # 1️⃣ First: draw ALL OTHER conferences
    for logo_path in other_logos:
        paste_random_logo(canvas, logo_path, WIDTH, HEIGHT)

    # 2️⃣ Second: draw SEC logos on TOP
    for logo_path in sec_logos:
        paste_random_logo(canvas, logo_path, WIDTH, HEIGHT)

    # Save result
    out_dir = ensure_output_dir()
    out_path = os.path.join(out_dir, f"STICKERBOMB_{wallpaper_type}.png")
    canvas.save(out_path)
    return out_path

if __name__ == "__main__":
    print("Generating PC sticker bomb...")
    path_pc = generate_sticker_bomb(conferences=None, wallpaper_type="pc")
    print("Saved:", path_pc)

    print("Generating Mobile sticker bomb...")
    path_mobile = generate_sticker_bomb(conferences=None, wallpaper_type="mobile")
    print("Saved:", path_mobile)
