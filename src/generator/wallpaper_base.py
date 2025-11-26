import os
import math
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import binary_dilation
import numpy as np


# ---------------------------------------------------------
#  PATH HELPER
# ---------------------------------------------------------

def asset_path(relative_path):
    """
    Returns an absolute filesystem path inside the project.
    """
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    return os.path.join(base, relative_path)


# ---------------------------------------------------------
#  COLOR HELPERS
# ---------------------------------------------------------

def hex_to_rgb(hex_color):
    if not hex_color:
        return None
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def darken(rgb, pct):
    r, g, b = rgb
    return (
        max(0, r + pct),
        max(0, g + pct),
        max(0, b + pct),
    )


# ---------------------------------------------------------
#  LOGO LOADING (MAIN + SMALL)
# ---------------------------------------------------------

def load_logo(path, max_width):
    """
    Loads a PNG logo and scales it down preserving aspect ratio.
    Always returns RGBA.
    """
    path = asset_path(path) if not os.path.isabs(path) else path

    img = Image.open(path).convert("RGBA")
    w, h = img.size

    if w > max_width:
        ratio = max_width / w
        img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)

    return img


def load_small_logo(path, max_size=150):
    """
    Loads an opponent/team logo safely.
    If missing, falls back to fallback.png.
    """
    absolute_path = asset_path(path) if not os.path.isabs(path) else path
    fallback_path = asset_path("data/logos/fallback.png")

    if not os.path.exists(absolute_path):
        absolute_path = fallback_path

    img = Image.open(absolute_path).convert("RGBA")
    img.thumbnail((max_size, max_size), Image.LANCZOS)
    return img


# ---------------------------------------------------------
#  PERFECT WHITE OUTLINE STROKE
# ---------------------------------------------------------

def add_logo_stroke(img, stroke_size=6, stroke_color=(255, 255, 255)):
    """
    Creates a clean, crisp outline stroke around the logo.
    No blur, no softness.
    """

    if img.mode != "RGBA":
        img = img.convert("RGBA")

    w, h = img.size

    # Extract alpha channel
    alpha = img.split()[3]

    # Create a mask of the stroke (solid dilation)
    import numpy as np
    alpha_np = np.array(alpha)

    # Create structuring element for dilation
    from scipy.ndimage import binary_dilation

    mask = alpha_np > 0
    stroke_mask = binary_dilation(mask, iterations=stroke_size)

    # Convert back to image
    stroke_img = Image.new("RGBA", (w, h), stroke_color + (0,))
    stroke_alpha = Image.fromarray((stroke_mask * 255).astype("uint8"))
    stroke_img.putalpha(stroke_alpha)

    # Composite stroke BELOW the logo
    out = Image.new("RGBA", (w, h))
    out.alpha_composite(stroke_img)
    out.alpha_composite(img)

    return out



# ---------------------------------------------------------
#  TEAM COLOR EXTRACTION (AVERAGE)
# ---------------------------------------------------------

def get_team_colors_from_logo(logo_path):
    path = asset_path(logo_path)
    img = Image.open(path).convert("RGB")
    pixels = list(img.getdata())
    r = sum(p[0] for p in pixels) // len(pixels)
    g = sum(p[1] for p in pixels) // len(pixels)
    b = sum(p[2] for p in pixels) // len(pixels)
    primary = (r, g, b)
    secondary = (max(r - 40, 0), max(g - 40, 0), max(b - 40, 0))
    return primary, secondary


# ---------------------------------------------------------
#  SOLID BACKGROUND
# ---------------------------------------------------------

def create_solid_background(width, height, color):
    return Image.new("RGB", (width, height), color)


# ---------------------------------------------------------
#  GRADIENT GENERATORS
# ---------------------------------------------------------

def create_linear_gradient(width, height, color1, color2, angle):
    diag = int(math.sqrt(width ** 2 + height ** 2))
    base = Image.new("RGB", (diag, diag))
    draw = ImageDraw.Draw(base)

    for y in range(diag):
        t = y / (diag - 1)
        r = int(color1[0] * (1 - t) + color2[0] * t)
        g = int(color1[1] * (1 - t) + color2[1] * t)
        b = int(color1[2] * (1 - t) + color2[2] * t)
        draw.line([(0, y), (diag, y)], fill=(r, g, b))

    rotated = base.rotate(angle, expand=True)
    cx, cy = rotated.width // 2, rotated.height // 2
    return rotated.crop((cx - width // 2, cy - height // 2,
                         cx + width // 2, cy + height // 2))


def create_radial_gradient(width, height, color1, color2):
    img = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(img)
    diag = math.sqrt((width / 2) ** 2 + (height / 2) ** 2)

    for y in range(height):
        for x in range(width):
            dist = math.sqrt((x - width / 2) ** 2 + (y - height / 2) ** 2)
            t = min(dist / diag, 1)
            r = int(color1[0] * (1 - t) + color2[0] * t)
            g = int(color1[1] * (1 - t) + color2[1] * t)
            b = int(color1[2] * (1 - t) + color2[2] * t)
            draw.point((x, y), (r, g, b))

    return img


def create_diamond_gradient(width, height, color1, color2):
    img = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(img)
    maxdist = width / 2 + height / 2

    for y in range(height):
        for x in range(width):
            t = (abs(x - width / 2) + abs(y - height / 2)) / maxdist
            t = min(max(t, 0), 1)
            r = int(color1[0] * (1 - t) + color2[0] * t)
            g = int(color1[1] * (1 - t) + color2[1] * t)
            b = int(color1[2] * (1 - t) + color2[2] * t)
            draw.point((x, y), (r, g, b))

    return img


def create_fade_gradient(width, height, color1):
    color2 = darken(color1, -40)
    img = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(img)

    for y in range(height):
        t = y / (height - 1)
        r = int(color1[0] * (1 - t) + color2[0] * t)
        g = int(color1[1] * (1 - t) + color2[1] * t)
        b = int(color1[2] * (1 - t) + color2[2] * t)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    return img


def create_split_gradient(width, height, color1, color2, angle):
    diag = int(math.sqrt(width ** 2 + height ** 2))
    img = Image.new("RGB", (diag, diag))
    draw = ImageDraw.Draw(img)

    mid = diag // 2
    for y in range(diag):
        draw.line([(0, y), (diag, y)], fill=color1 if y < mid else color2)

    rotated = img.rotate(angle, expand=True)
    cx, cy = rotated.width // 2, rotated.height // 2
    return rotated.crop((cx - width // 2, cy - height // 2,
                         cx + width // 2, cy + height // 2))


def create_mirror_gradient(width, height, color1, color2, angle):
    diag = int(math.sqrt(width ** 2 + height ** 2))
    img = Image.new("RGB", (diag, diag))
    draw = ImageDraw.Draw(img)
    mid = diag // 2

    for y in range(diag):
        t = y / mid if y <= mid else (diag - y) / mid
        t = max(0, min(t, 1))
        r = int(color1[0] * (1 - t) + color2[0] * t)
        g = int(color1[1] * (1 - t) + color2[1] * t)
        b = int(color1[2] * (1 - t) + color2[2] * t)
        draw.line([(0, y), (diag, y)], fill=(r, g, b))

    rotated = img.rotate(angle, expand=True)
    cx, cy = rotated.width // 2, rotated.height // 2
    return rotated.crop((cx - width // 2, cy - height // 2,
                         cx + width // 2, cy + height // 2))


# ---------------------------------------------------------
#  NOISE (PERLIN STYLE)
# ---------------------------------------------------------

def generate_perlin_noise(width, height, scale=16):
    grid_x = width // scale + 2
    grid_y = height // scale + 2

    rand_grid = np.random.rand(grid_y, grid_x)
    noise = np.zeros((height, width))

    for y in range(height):
        for x in range(width):
            gx, gy = x / scale, y / scale
            x0, y0 = int(gx), int(gy)
            x1, y1 = x0 + 1, y0 + 1

            sx, sy = gx - x0, gy - y0

            n0 = rand_grid[y0, x0] * (1 - sx) + rand_grid[y0, x1] * sx
            n1 = rand_grid[y1, x0] * (1 - sx) + rand_grid[y1, x1] * sx

            noise[y, x] = n0 * (1 - sy) + n1 * sy

    noise = (noise - noise.min()) / (noise.max() - noise.min())
    return noise


def create_noise_gradient(width, height, color1, color2, scale=16):
    noise = generate_perlin_noise(width, height, scale=scale)
    img = Image.new("RGB", (width, height))

    for y in range(height):
        for x in range(width):
            t = noise[y, x]
            r = int(color1[0] * (1 - t) + color2[0] * t)
            g = int(color1[1] * (1 - t) + color2[1] * t)
            b = int(color1[2] * (1 - t) + color2[2] * t)
            img.putpixel((x, y), (r, g, b))

    return img


# ---------------------------------------------------------
#  GRADIENT DISPATCHER
# ---------------------------------------------------------

def create_gradient(width, height, style, color1, color2, angle, **kwargs):
    noise_detail = int(kwargs.get("noise_detail", 2))
    noise_scale = 32 if noise_detail == 1 else 8 if noise_detail == 3 else 16

    if style == "linear":
        return create_linear_gradient(width, height, color1, color2, angle)

    if style == "radial":
        return create_radial_gradient(width, height, color1, color2)

    if style == "diamond":
        return create_diamond_gradient(width, height, color1, color2)

    if style == "fade":
        return create_fade_gradient(width, height, color1)

    if style == "split":
        return create_split_gradient(width, height, color1, color2, angle)

    if style == "mirror":
        return create_mirror_gradient(width, height, color1, color2, angle)

    if style == "noise":
        return create_noise_gradient(width, height, color1, color2, scale=noise_scale)

    return create_linear_gradient(width, height, color1, color2, angle)
