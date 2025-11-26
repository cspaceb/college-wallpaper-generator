from src.generator.wallpaper_pc import generate_pc_wallpaper
from src.generator.wallpaper_mobile import generate_mobile_wallpaper

dummy_schedule = [
    {"week": 1, "opponent": "Texas", "home": True, "date": "08-31"},
    {"week": 2, "opponent": "Auburn", "home": False, "date": "09-07"},
    {"week": 3, "opponent": "LSU", "home": True, "date": "09-14"},
    {"week": 4, "opponent": "Georgia", "home": False, "date": "09-21"},
    {"week": 5, "opponent": "Tennessee", "home": True, "date": "09-28"},
    {"week": 6, "opponent": "Florida", "home": False, "date": "10-05"},
    {"week": 7, "opponent": "Ole Miss", "home": True, "date": "10-12"},
    {"week": 9, "opponent": "Kentucky", "home": True, "date": "10-26"},
    {"week": 10, "opponent": "Arkansas", "home": False, "date": "11-02"},
    {"week": 11, "opponent": "Texas A&M", "home": True, "date": "11-09"},
    {"week": 12, "opponent": "Mississippi State", "home": False, "date": "11-16"},
    {"week": 13, "opponent": "Vanderbilt", "home": True, "date": "11-23"},
]


pc_path = generate_pc_wallpaper(
    "Alabama",
    dummy_schedule,
    "data/logos/Alabama.png"
)
print("Generated PC:", pc_path)

mobile_path = generate_mobile_wallpaper(
    "Alabama",
    dummy_schedule,
    "data/logos/Alabama.png"
)
print("Generated Mobile:", mobile_path)
