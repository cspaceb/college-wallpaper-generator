import os
import json
import re
from difflib import SequenceMatcher   # <-- FIXED


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "..", "data")

TEAMS_JSON = os.path.join(DATA_DIR, "teams_2025.json")
LOGO_DIR = os.path.join(DATA_DIR, "logos")

# ============================================================
# LOAD TEAMS & LOGOS
# ============================================================

with open(TEAMS_JSON, "r", encoding="utf-8") as f:
    TEAMS_2025 = json.load(f)

ALL_LOGOS = [f for f in os.listdir(LOGO_DIR) if f.lower().endswith(".png")]

# ============================================================
# NORMALIZATION HELPERS
# ============================================================

def simplify(s: str) -> str:
    """Normalize a name for fuzzy comparison."""
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)  # non-letters → underscore
    return s.strip("_")

def tokens(s: str):
    """Split normalized name into tokens."""
    return simplify(s).split("_")

# ============================================================
# FUZZY MATCHING (IMPROVED)
# ============================================================

def fuzzy_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def is_alt_logo(fname):
    alt_terms = ("alt", "secondary", "wordmark", "logo2", "logo3", "dark")
    name = fname.lower()
    return any(t in name for t in alt_terms)

def match_logo_to_team(team_name: str):
    """
    BEST POSSIBLE MATCHING:
        1. Exact normalized match
        2. Token-overlap > 0.5
        3. Fuzzy similarity >= 0.65
        4. Prefer filenames with no numbers
        5. Avoid alt/wordmark logos
        6. Enforce uniqueness at final stage
    """

    base = simplify(team_name)
    base_tokens = set(tokens(team_name))

    # 1. Direct exact matches
    exact_match = f"{team_name.replace(' ', '_')}.png"
    if exact_match in ALL_LOGOS:
        return exact_match

    # 2. Token-overlap scoring
    candidates = []
    for fname in ALL_LOGOS:
        stem = simplify(fname.replace(".png", ""))
        tks = set(stem.split("_"))

        overlap = len(base_tokens & tks) / max(len(base_tokens), 1)

        # must share at least one word
        if overlap < 0.34:
            continue

        score = fuzzy_similarity(base, stem)
        if score >= 0.50:
            candidates.append((score, overlap, fname))

    if not candidates:
        # fallback fuzzy
        scored = []
        for fname in ALL_LOGOS:
            stem = simplify(fname.replace(".png", ""))
            score = fuzzy_similarity(base, stem)
            scored.append((score, fname))
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1]

    # Sort by:
    #   similarity → token overlap → no-numbers → non-alt → filename length
    def sort_key(item):
        score, overlap, fname = item
        has_numbers = bool(re.search(r"[0-9]", fname))
        return (
            -score,
            -overlap,
            has_numbers,
            is_alt_logo(fname),
            len(fname)
        )

    candidates.sort(key=sort_key)
    return candidates[0][2]


# ============================================================
# CONFERENCE NORMALIZATION (Option A)
# ============================================================

CONFERENCE_REMAP = {
    "American Athletic": "AAC",
    "Conference USA": "C-USA",
    "Mid-American": "Mid-American",
    "Mountain West": "Mountain West",
    "Sun Belt": "Sun Belt",

    "ACC": "ACC",
    "Big Ten": "Big Ten",
    "Big 12": "Big 12",
    "SEC": "SEC",
}

P4 = ["ACC", "Big Ten", "Big 12", "SEC"]
G5 = ["AAC", "C-USA", "Mid-American", "Mountain West", "Sun Belt"]
ALL_CONFERENCES = P4 + G5

# ============================================================
# BUILD THE CONFERENCE MAP
# ============================================================

# Temp structure: before duplicate-resolution
TEMP_CONF_LOGOS = {c: [] for c in ALL_CONFERENCES}

for team in TEAMS_2025:
    school = team["school"]
    raw_conf = team["conference"]

    if raw_conf not in CONFERENCE_REMAP:
        continue  # skip independents

    conf = CONFERENCE_REMAP[raw_conf]
    TEMP_CONF_LOGOS[conf].append(school)


# Now resolve each school → correct logo, ensuring NO duplicates
USED_LOGOS = set()
CONFERENCE_MAP = {c: [] for c in ALL_CONFERENCES}

for conf, schools in TEMP_CONF_LOGOS.items():
    for school in sorted(schools):
        logo = match_logo_to_team(school)

        # enforce uniqueness
        if logo in USED_LOGOS:
            # if duplicate, try next-best fuzzy alternative
            alts = []
            base = simplify(school)
            for fname in ALL_LOGOS:
                stem = simplify(fname.replace(".png", ""))
                score = fuzzy_similarity(base, stem)
                if 0.65 <= score <= 0.95:  # different but similar
                    alts.append((score, fname))

            if alts:
                alts.sort(key=lambda x: -x[0])
                for _, alt_logo in alts:
                    if alt_logo not in USED_LOGOS:
                        logo = alt_logo
                        break

        USED_LOGOS.add(logo)

        CONFERENCE_MAP[conf].append({
            "name": school,
            "logo": logo
        })


# ============================================================
# PUBLIC API
# ============================================================

def get_teams_by_conference(conf_name: str):
    return CONFERENCE_MAP.get(conf_name, [])


def get_all_conferences():
    return ALL_CONFERENCES


# Optional debug
if __name__ == "__main__":
    print("Conferences Loaded:", ALL_CONFERENCES)
    for c in ALL_CONFERENCES:
        print(f"\n=== {c} ===")
        for t in CONFERENCE_MAP[c]:
            print(f"{t['name']}  ->  {t['logo']}")
