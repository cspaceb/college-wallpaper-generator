# --- File: src/generator/sticker_bomb.py
import os
import random
from PIL import Image, ImageFilter, ImageOps
from src.generator.wallpaper_base import asset_path, load_small_logo

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

def ensure_output_dir():
    """
    Ensures that the /output directory exists and returns its absolute path.
    Mirrors the behavior in your wallpaper generator.
    """
    base = asset_path("output")
    if not os.path.exists(base):
        os.makedirs(base, exist_ok=True)
    return base

# ============================================================
# ADD DIE-CUT STYLE STICKER BORDER
# ============================================================

def add_sticker_border(logo: Image.Image, border_size=22):
    """
    Adds a clean white die-cut sticker border around a logo PNG.
    The border follows the exact alpha outline of the logo.
    """
    logo = logo.convert("RGBA")

    # Extract alpha channel
    alpha = logo.split()[3]

    # Expand mask outward
    expanded = alpha.filter(ImageFilter.GaussianBlur(border_size / 3))

    # Convert blurred mask to solid white border
    bw = expanded.point(lambda p: 255 if p > 10 else 0)

    # Create white silhouette
    border_layer = Image.new("RGBA", logo.size, (255, 255, 255, 255))
    border_layer.putalpha(bw)

    # Composite the original logo on top
    bordered_logo = Image.alpha_composite(border_layer, logo)

    return bordered_logo


# ============================================================
# LOAD LOGOS
# ============================================================

def get_all_logos():
    logos_dir = asset_path("data/logos")
    return [
        os.path.join(logos_dir, f)
        for f in os.listdir(logos_dir)
        if f.lower().endswith(".png") and f != "fallback.png"
    ]


# ============================================================
# SPLIT SEC TEAMS
# ============================================================

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


# ============================================================
# PASTE LOGOS
# ============================================================

def paste_random_logo(canvas, logo_path, WIDTH, HEIGHT):
    """Helper to paste a logo multiple times with random size/rotation."""
    for _ in range(random.randint(5, 8)):
        try:
            size = random.randint(70, 180)

            # Load and resize logo
            logo = load_small_logo(logo_path, max_size=size)

            # Apply sticker border
            logo = add_sticker_border(logo, border_size=12)

            # Rotate for randomness
            logo = logo.rotate(random.randint(-25, 25), expand=True)

            # Random placement
            x = random.randint(0, WIDTH - logo.width)
            y = random.randint(0, HEIGHT - logo.height)

            canvas.paste(logo, (x, y), logo)

        except Exception:
            continue


# ============================================================
# GENERATOR
# ============================================================

def generate_sticker_bomb(conferences, wallpaper_type):
    if wallpaper_type not in SIZES:
        raise ValueError("Invalid type. Use 'pc' or 'mobile'.")

    WIDTH, HEIGHT = SIZES[wallpaper_type]
    canvas = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)

    logos = get_all_logos()
    if not logos:
        raise ValueError("No logos found.")

    # Split into SEC on top
    sec_logos, other_logos = split_sec_and_others(logos)

    # Randomize both groups
    random.shuffle(other_logos)
    random.shuffle(sec_logos)

    # 1️⃣ Draw all other conferences first
    for logo_path in other_logos:
        paste_random_logo(canvas, logo_path, WIDTH, HEIGHT)

    # 2️⃣ Draw SEC logos last (on top)
    for logo_path in sec_logos:
        paste_random_logo(canvas, logo_path, WIDTH, HEIGHT)

    # Save result
    out_dir = ensure_output_dir()
    out_path = os.path.join(out_dir, f"STICKERBOMB_{wallpaper_type}.png")
    canvas.save(out_path)
    return out_path


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("Generating PC sticker bomb...")
    path_pc = generate_sticker_bomb(conferences=None, wallpaper_type="pc")
    print("Saved:", path_pc)

    print("Generating Mobile sticker bomb...")
    path_mobile = generate_sticker_bomb(conferences=None, wallpaper_type="mobile")
    print("Saved:", path_mobile)
