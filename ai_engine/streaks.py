from datetime import date, timedelta, datetime


# ---------------------------------
# CALCULATE STREAK (SAFE VERSION)
# ---------------------------------

def calculate_streak(dates):

    if not dates:
        return 0

    # 🔥 convert strings → date objects (IMPORTANT)
    cleaned_dates = []

    for d in dates:
        if isinstance(d, str):
            cleaned_dates.append(datetime.strptime(d, "%Y-%m-%d").date())
        else:
            cleaned_dates.append(d)

    dates = sorted(set(cleaned_dates), reverse=True)

    today = date.today()

    # 🔥 if last activity not today or yesterday → no streak
    if dates[0] != today and dates[0] != today - timedelta(days=1):
        return 0

    streak = 1

    for i in range(len(dates) - 1):

        if dates[i] - dates[i + 1] == timedelta(days=1):
            streak += 1
        else:
            break

    return streak


# ---------------------------------
# STREAK BONUS (UNCHANGED)
# ---------------------------------

def streak_bonus(streak):

    if streak >= 30:
        return 50
    elif streak >= 14:
        return 30
    elif streak >= 7:
        return 20
    elif streak >= 3:
        return 10
    else:
        return 0