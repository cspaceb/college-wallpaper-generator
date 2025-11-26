import os
import random
from PIL import Image, ImageFilter
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
# HIGH-QUALITY STICKER BORDER
# ============================================================

def add_sticker_border(logo: Image.Image, border_size=2):
    """
    Adds a clean white die-cut sticker border around a logo PNG.
    High-quality, sharp edge version.
    """
    logo = logo.convert("RGBA")

    # Extract alpha channel
    alpha = logo.split()[3]

    # Slight blur for expansion – reduced for sharpness
    expanded = alpha.filter(ImageFilter.GaussianBlur(border_size / 4))

    # High threshold for crisp border
    bw = expanded.point(lambda p: 255 if p > 5 else 0)

    # Create white silhouette
    border_layer = Image.new("RGBA", logo.size, (255, 255, 255, 255))
    border_layer.putalpha(bw)

    # Composite original logo on top
    bordered_logo = Image.alpha_composite(border_layer, logo)

    return bordered_logo


# ============================================================
# LOAD ALL LOGOS
# ============================================================

def get_all_logos():
    logos_dir = asset_path("data/logos")
    return [
        os.path.join(logos_dir, f)
        for f in os.listdir(logos_dir)
        if f.lower().endswith(".png") and f != "fallback.png"
    ]


# ============================================================
# HIGH-QUALITY PASTE LOGO
# ============================================================

def paste_random_logo(canvas, logo_path, WIDTH, HEIGHT):
    """Past 5–8 logos with crisp edges, sharp rotation, and border."""
    for _ in range(random.randint(5, 8)):
        try:
            size = random.randint(70, 180)

            # Load & resize with highest quality filter
            logo = load_small_logo(logo_path, max_size=size)
            logo = logo.resize(
                (logo.width, logo.height),
                resample=Image.Resampling.LANCZOS
            )

            # Add clean sticker-style border
            logo = add_sticker_border(logo, border_size=10)

            # High-quality rotation
            logo = logo.rotate(
                random.randint(-25, 25),
                expand=True,
                resample=Image.Resampling.BICUBIC
            )

            # Random placement
            x = random.randint(0, WIDTH - logo.width)
            y = random.randint(0, HEIGHT - logo.height)

            canvas.paste(logo, (x, y), logo)

        except Exception:
            continue


# ============================================================
# GENERATOR
# ============================================================

def generate_stickerbomb(type_):
    if type_ not in TARGET_SIZES:
        raise ValueError("Invalid type: 'pc' or 'mobile'")

    TRIM_W, TRIM_H = TARGET_SIZES[type_]

    # Oversized work canvas for dense randomness
    WORK_W = int(TRIM_W * SCALE)
    WORK_H = int(TRIM_H * SCALE)

    print(f"[{type_}] Creating work canvas {WORK_W} × {WORK_H}")

    canvas = Image.new("RGB", (WORK_W, WORK_H), BG_COLOR)

    # Load & shuffle logos
    logos = get_all_logos()
    random.shuffle(logos)

    # Paste logos with improved quality
    for logo_path in logos:
        paste_random_logo(canvas, logo_path, WORK_W, WORK_H)

    # Crop to final resolution
    left = (WORK_W - TRIM_W) // 2
    top = (WORK_H - TRIM_H) // 2
    right = left + TRIM_W
    bottom = top + TRIM_H

    final_img = canvas.crop((left, top, right, bottom))

    # SAVE INTO /data/stickerbomb
    save_dir = asset_path("data/stickerbomb")
    os.makedirs(save_dir, exist_ok=True)

    filename = "pc.png" if type_ == "pc" else "mobile.png"
    out_path = os.path.join(save_dir, filename)

    final_img.save(out_path)
    print(f"[DONE] Saved: {out_path}")
    return out_path


# ============================================================
# MAIN EXECUTION
# ============================================================

if __name__ == "__main__":
    generate_stickerbomb("pc")
    generate_stickerbomb("mobile")
