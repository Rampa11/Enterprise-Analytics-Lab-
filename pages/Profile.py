import streamlit as st
from auth import supabase
from ai_engine.badges import check_badges
from ai_engine.streaks import calculate_streak, streak_bonus
from datetime import datetime

st.title("👤 Profile")

# ---------------------------------
# CHECK LOGIN
# ---------------------------------
user_id = st.session_state.get("user_id")

if not user_id:
    st.warning("Please login first")
    st.stop()

# ---------------------------------
# FETCH USER DATA (LEADERBOARD)
# ---------------------------------
res = supabase.table("leaderboard") \
    .select("*") \
    .eq("user_email", st.session_state.get("user")) \
    .execute()

data = res.data if res.data else []

# ---------------------------------
# PROFILE SUMMARY
# ---------------------------------
st.markdown("### 📊 Your Activity")

if len(data) > 0:

    total_challenges = len(data)
    best_score = max([d.get("score", 0) for d in data])

    st.write(f"Total Challenges: {total_challenges}")
    st.write(f"Best Score: {best_score}")

    # ---------------------------------
    # PREP DATA
    # ---------------------------------
    industries = [d.get("industry") for d in data if d.get("industry")]

    dates = []
    for d in data:
        date_val = d.get("date_completed")
        if date_val:
            try:
                dates.append(datetime.fromisoformat(date_val).date())
            except:
                pass

    # ---------------------------------
    # STREAK
    # ---------------------------------
    streak = calculate_streak(dates)
    bonus_xp = streak_bonus(streak)

    st.markdown("---")
    st.subheader("🔥 Daily Practice Streak")
    st.success(f"{streak} day streak")

    if bonus_xp > 0:
        st.info(f"Streak bonus XP: +{bonus_xp}")

    # ---------------------------------
    # BADGES
    # ---------------------------------
    badges = check_badges(
        total_challenges=total_challenges,
        best_score=best_score,
        industries=industries
    )

    st.markdown("---")
    st.subheader("🏆 Badges Earned")

    badge_icons = {
        "🏁 First Challenge": "🥇",
        "📈 Rising Analyst": "🚀",
        "🏆 Top Performer": "🔥",
        "🌍 Multi-Industry Analyst": "🌍",
        "🧠 AI Strategist": "🧠"
    }

    if len(badges) == 0:
        st.info("No badges yet.")

    else:
        for badge in badges:
            icon = badge_icons.get(badge, "🏅")
            st.success(f"{icon} {badge}")

else:
    st.markdown("---")

    st.subheader("🔥 Daily Practice Streak")
    st.info("Complete a challenge to start your streak.")

    st.subheader("🏆 Badges Earned")
    st.info("Complete challenges to earn badges.")