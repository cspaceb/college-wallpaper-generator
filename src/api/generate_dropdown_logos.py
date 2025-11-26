import os
from PIL import Image, ImageChops
from src.generator.wallpaper_base import asset_path, load_small_logo


# ------------------------------------------------------------
# PERFECT 1PX STROKE FOR PNG TRANSPARENCY (FOR SMALL ICONS)
# ------------------------------------------------------------
def add_1px_stroke(img, stroke_color=(255, 255, 255)):
    """
    Adds a CLEAN 1px outline around a logo based on its alpha channel.
    This method offsets the alpha mask in 8 directions, producing
    a crisp sprite-style outline instead of the thick blur from MaxFilter.

    Works perfectly at small sizes like 24px–40px.
    """

    if img.mode != "RGBA":
        img = img.convert("RGBA")

    w, h = img.size
    alpha = img.split()[3]  # transparency mask

    # Output canvas
    outline = Image.new("L", (w, h), 0)

    # 8 directions for a 1px outline
    offsets = [
        (-1, 0), (1, 0),
        (0, -1), (0, 1),
        (-1, -1), (-1, 1),
        (1, -1), (1, 1)
    ]

    for dx, dy in offsets:
        shifted = Image.new("L", (w, h), 0)
        shifted.paste(alpha, (dx, dy))
        outline = ImageChops.lighter(outline, shifted)

    # Stroke layer
    stroke_layer = Image.new("RGBA", (w, h), stroke_color)
    stroke_layer.putalpha(outline)

    # Composite stroke under original logo
    result = Image.alpha_composite(stroke_layer, img)

    return result


# ------------------------------------------------------------
# GENERATE DROPDOWN ICONS
# ------------------------------------------------------------
def generate_dropdown_logos():
    logos_dir = asset_path("data/logos")
    out_dir = asset_path("data/logos_dropdown")

    os.makedirs(out_dir, exist_ok=True)

    max_size = 32  # perfect UI size

    print(f"Generating dropdown logos from: {logos_dir}")
    print(f"Saving stroked logos to: {out_dir}\n")

    for file in os.listdir(logos_dir):
        if not file.lower().endswith(".png"):
            continue

        input_path = os.path.join(logos_dir, file)
        output_path = os.path.join(out_dir, file)

        try:
            img = load_small_logo(input_path, max_size=max_size)
            img = add_1px_stroke(img)  # pixel-perfect 1px outline
            img.save(output_path)

            print("[OK]", file)

        except Exception as e:
            print("[ERROR]", file, e)

    print("\n✔ Done generating dropdown icons!")


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------
if __name__ == "__main__":
    generate_dropdown_logos()
