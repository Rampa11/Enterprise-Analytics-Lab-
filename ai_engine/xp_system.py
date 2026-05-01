# ---------------------------------
# XP CALCULATION (SAFE)
# ---------------------------------

def calculate_xp(score):

    try:
        score = int(score)
    except:
        return 0  # fallback if invalid

    if score >= 90:
        return 50
    elif score >= 80:
        return 30
    elif score >= 70:
        return 20
    else:
        return 10


# ---------------------------------
# LEVEL SYSTEM (IMPROVED)
# ---------------------------------

def determine_level(total_xp):

    if total_xp < 100:
        return {
            "level": "Data Intern",
            "next_level_xp": 100
        }

    elif total_xp < 250:
        return {
            "level": "Junior Analyst",
            "next_level_xp": 250
        }

    elif total_xp < 500:
        return {
            "level": "Senior Analyst",
            "next_level_xp": 500
        }

    elif total_xp < 800:
        return {
            "level": "Analytics Manager",
            "next_level_xp": 800
        }

    else:
        return {
            "level": "Chief Data Officer",
            "next_level_xp": None
        }