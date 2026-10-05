"""Server-owned results. Guests use explicit, temporary session storage."""
from datetime import datetime, timezone, timedelta
import hashlib
import logging
import streamlit as st
from supabase import create_client
from auth import current_user, verify_user, get_client
from lab.config import setting

log = logging.getLogger(__name__)

def admin_client():
    url, key = setting("SUPABASE_URL"), setting("SUPABASE_SERVICE_ROLE_KEY")
    return create_client(url,key) if url and key else None

def guest_history():
    return st.session_state.setdefault("guest_history", [])

def ensure_profile():
    if not current_user():
        return
    user = verify_user()
    admin = admin_client()
    if admin is None:
        raise RuntimeError("Saved progress is not configured yet. You can still practice in this session.")
    # Only insert if absent: never reset paid entitlements on login.
    found = admin.table("lab_profiles").select("user_id").eq("user_id",user.id).execute().data
    if not found:
        alias = "Analyst " + hashlib.sha256(user.id.encode()).hexdigest()[:6].upper()
        admin.table("lab_profiles").upsert({"user_id":user.id,"display_name":alias},on_conflict="user_id",ignore_duplicates=True).execute()

def profile():
    fallback = {"plan":"free","credits":0,"display_name":"Guest analyst","premium_until":None}
    if not current_user():
        return fallback
    try:
        rows = get_client().table("lab_profiles").select("*").eq("user_id",current_user()["id"]).execute().data
        if rows:
            result = rows[0]
            until = result.get("premium_until")
            if until and datetime.fromisoformat(until.replace("Z","+00:00")) <= datetime.now(timezone.utc):
                result["plan"] = "free"
            return result
    except Exception:
        log.warning("Profile read unavailable")
    return {**fallback,"display_name":current_user().get("name","Analyst")}

def history():
    if not current_user():
        return guest_history()
    try:
        user = verify_user()
        admin = admin_client()
        if admin is None:
            raise RuntimeError("Storage not configured")
        rows = []
        offset = 0
        while True:
            batch = admin.table("lab_attempts").select("*").eq("user_id",user.id).order("completed_at",desc=True).range(offset,offset+999).execute().data
            rows.extend(batch)
            if len(batch)<1000:
                return rows
            offset += 1000
    except Exception:
        st.warning("Saved progress is temporarily unavailable. Your current result remains on this page.")
        return []

def save_attempt(task, answer, result):
    score = result.get("score")
    if not isinstance(score,int) or isinstance(score,bool) or not 0 <= score <= 100:
        raise ValueError("Only validated scores can be saved.")
    record = dict(challenge_id=task["id"],title=task["title"],industry=task["industry"],kind=task["kind"],dataset_id=task["dataset_id"],
                  score=score,xp=round(score*(1.5 if task["kind"]=="manager" else 1)),answer=answer,result=result,
                  completed_at=datetime.now(timezone.utc).isoformat())
    if not current_user():
        rows = guest_history()
        previous = next((r for r in rows if r["challenge_id"]==task["id"]),None)
        if previous and previous["score"] >= score:
            return False
        rows[:] = [r for r in rows if r["challenge_id"]!=task["id"]]
        rows.insert(0,record)
        return True
    user = verify_user()
    admin = admin_client()
    if admin is None:
        raise RuntimeError("Could not save to your account. Please retry when account storage is available.")
    # Atomic best-score upsert. Retrying cannot award duplicate XP.
    response = admin.rpc("lab_save_attempt",{"p_user_id":user.id,"p_record":record}).execute()
    return bool(response.data)

def unlock(challenge_id):
    user = verify_user()
    admin = admin_client()
    if admin is None:
        raise RuntimeError("Answer credits are unavailable.")
    return bool(admin.rpc("lab_unlock_answer",{"p_user_id":user.id,"p_challenge_id":challenge_id}).execute().data)

def is_unlocked(challenge_id):
    if profile()["plan"]=="premium":
        return True
    if not current_user():
        return False
    try:
        return bool(get_client().table("lab_unlocks").select("challenge_id").eq("user_id",current_user()["id"]).eq("challenge_id",challenge_id).execute().data)
    except Exception:
        return False

def leaderboard():
    client = admin_client()
    if not client:
        return []
    try:
        return client.rpc("lab_leaderboard").execute().data or []
    except Exception:
        return []

def stats(rows, today=None):
    today = today or datetime.now(timezone.utc).date()
    days = {datetime.fromisoformat(r["completed_at"].replace("Z","+00:00")).date() for r in rows}
    cursor = today if today in days else today-timedelta(days=1)
    streak = 0
    while cursor in days:
        streak += 1
        cursor -= timedelta(days=1)
    xp = sum(r["xp"] for r in rows)
    return dict(completed=len(rows),xp=xp,average=round(sum(r["score"] for r in rows)/len(rows)) if rows else 0,
                streak=streak,level=1+xp//500,level_progress=(xp%500)/500)

def badges(rows):
    s = stats(rows)
    return [
        ("First insight","Complete your first challenge",s["completed"]>=1),
        ("Finding your rhythm","Complete 10 distinct challenges",s["completed"]>=10),
        ("Sharp eye","Score at least 90 on a challenge",any(r["score"]>=90 for r in rows)),
        ("Industry explorer","Practice across 3 industries",len({r["industry"] for r in rows})>=3),
        ("On a roll","Build a 3-day practice streak",s["streak"]>=3)]


def reserve_ai_call():
    user = verify_user()
    admin = admin_client()
    if admin is None:
        raise RuntimeError("AI coaching needs account storage to be connected.")
    try:
        allowed = admin.rpc("lab_reserve_ai_call",{"p_user_id":user.id}).execute().data
    except Exception:
        raise RuntimeError("AI coaching is temporarily unavailable. Please try again later.") from None
    if not allowed:
        raise RuntimeError("Your daily AI allowance has been reached. Numerical practice is still available.")
