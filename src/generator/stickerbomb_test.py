import os
import random
from PIL import Image
from src.generator.wallpaper_base import asset_path, load_small_logo


# ============================================================
# TARGET SIZES
# ============================================================

TARGET_SIZES = {
    "pc": (2560, 1440),
    "mobile": (1284, 2778),
}

# Work canvas multiplier
SCALE = 1.35   # 35% larger background generation

BG_COLOR = (17, 17, 17)


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
# PASTE LOGOS LIKE ORIGINAL SYSTEM
# ============================================================

def paste_random_logo(canvas, logo_path, WIDTH, HEIGHT):
    """Place 5–8 logos randomly like your original code."""
    for _ in range(random.randint(5, 8)):
        try:
            size = random.randint(70, 180)
            logo = load_small_logo(logo_path, max_size=size)
            logo = logo.rotate(random.randint(-25, 25), expand=True)

            x = random.randint(0, WIDTH - logo.width)
            y = random.randint(0, HEIGHT - logo.height)

            canvas.paste(logo, (x, y), logo)
        except:
            continue


# ============================================================
# GENERATOR
# ============================================================

def generate_stickerbomb(type_):
    if type_ not in TARGET_SIZES:
        raise ValueError("Invalid type: 'pc' or 'mobile'")

    TRIM_W, TRIM_H = TARGET_SIZES[type_]

    # Oversized working canvas
    WORK_W = int(TRIM_W * SCALE)
    WORK_H = int(TRIM_H * SCALE)

    print(f"[{type_}] Creating work canvas {WORK_W} × {WORK_H}")

    canvas = Image.new("RGB", (WORK_W, WORK_H), BG_COLOR)

    # Load logos
    logos = get_all_logos()
    random.shuffle(logos)

    # Paste logos just like original logic
    for logo_path in logos:
        paste_random_logo(canvas, logo_path, WORK_W, WORK_H)

    # Now crop center to final size
    left = (WORK_W - TRIM_W) // 2
    top = (WORK_H - TRIM_H) // 2
    right = left + TRIM_W
    bottom = top + TRIM_H

    final_img = canvas.crop((left, top, right, bottom))

    out_path = f"stickerbomb_{type_}_cropped.png"
    final_img.save(out_path)

    print(f"[DONE] Saved: {out_path}")
    return out_path


# ============================================================
# STANDALONE EXECUTION
# ============================================================

if __name__ == "__main__":
    generate_stickerbomb("pc")
    generate_stickerbomb("mobile")
