# ---------------------------------
# BADGE SYSTEM (SAFE + CLEAN)
# ---------------------------------

def check_badges(total_challenges, best_score, industries):

    badges = []

    # 🔥 safe defaults
    total_challenges = total_challenges or 0
    best_score = best_score or 0
    industries = industries or []

    unique_industries = set(industries)

    # -----------------------------
    # BADGE RULES
    # -----------------------------

    if total_challenges >= 1:
        badges.append("🏁 First Challenge")

    if total_challenges >= 10:
        badges.append("📈 Rising Analyst")

    if total_challenges >= 50:
        badges.append("🧠 AI Strategist")

    if best_score >= 90:
        badges.append("🏆 Top Performer")

    if len(unique_industries) >= 3:
        badges.append("🌍 Multi-Industry Analyst")

    return badges