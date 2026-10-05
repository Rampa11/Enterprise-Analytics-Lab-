import json
import streamlit as st
from auth import current_user
from lab import storage
from lab.ai import review_answer
from lab.challenges import build_challenges,daily_challenge,check_answer
from lab.config import setting
from lab.datasets import CATALOG,load_dataset
from lab.ui import heading,active_data,explorer

def save_result(task,answer,result):
    try:
        storage.save_attempt(task,answer,result)
        st.session_state["saved_"+task["id"]+"_"+str(result["score"])]=True
    except Exception:
        st.warning("Your result is ready, but could not be saved to your account. Retry below; you will not be graded again.")

def render_result(task,result,answer,saved=False):
    with st.container(border=True):
        st.subheader("Your result")
        a,b=st.columns([1,3])
        a.metric("Score",f"{result['score']} / 100")
        b.write(result.get("feedback") or result.get("summary","Review complete."))
        st.caption(result.get("source","AI assessment · review the reasoning as well as the score"))
        if "segment_correct" in result:
            st.write(("✓" if result["segment_correct"] else "○")+" Segment identified")
            st.write(("✓" if result["value_correct"] else "○")+" Numerical value within 0.5% tolerance")
        unlocked=storage.is_unlocked(task["id"])
        if unlocked:
            if "method" in result:
                st.markdown("**Worked approach**")
                st.write(result["method"])
                st.write(result["answer"])
            else:
                st.markdown("**What worked**")
                for item in result.get("strengths",[]): st.write("• "+item)
                st.markdown("**What to improve**")
                for item in result.get("improvements",[]): st.write("• "+item)
                st.write(result.get("suggested_approach",""))
        else:
            st.caption("Full worked answers and detailed coaching are included with Premium, or unlock this challenge with one credit.")
            if current_user() and storage.profile()["credits"]>0:
                if st.button("Unlock full feedback · 1 credit",key="unlock_"+task["id"]):
                    try:
                        if storage.unlock(task["id"]): st.rerun()
                        else: st.warning("No credits available. Refresh your account after checkout.")
                    except Exception:
                        st.error("Could not unlock feedback. Please retry.")
            st.page_link("pages/Pricing.py",label="See learning plans",icon=":material/lock_open:")
        saved_key="saved_"+task["id"]+"_"+str(result["score"])
        if saved or st.session_state.get(saved_key):
            st.caption("Saved to your account." if current_user() else "Saved for this guest session.")
        elif st.button("Retry saving this result",key="retry_"+task["id"]):
            save_result(task,answer,result)
            st.rerun()
        export={"challenge":task["question"],"industry":task["industry"],"answer":answer,"score":result["score"],"feedback":result if unlocked else result.get("feedback",result.get("summary",""))}
        st.download_button("Download analysis record",json.dumps(export,indent=2),file_name="analysis_record.json",mime="application/json",key="export_"+task["id"])

def workbench(task,df):
    with st.container(border=True):
        st.caption(f"{task['difficulty'].upper()} · {task['industry'].upper()} · 10–15 MIN")
        st.subheader(task["title"])
        st.write(task["brief"])
        st.markdown("**Your question**")
        st.write(task["question"])
    with st.expander("Explore the dataset",expanded=True):
        explorer(df,task["industry"],key=task["id"])
    st.subheader("Build your answer")
    st.caption("Use the explorer or download the CSV for Excel, SQL, or Python. Report a value from the complete dataset.")
    with st.form("answer_"+task["id"]):
        a,b=st.columns(2)
        segment=a.selectbox("Your leading segment",task["options"],index=None,placeholder="Select a segment")
        value=b.text_input("Your calculated value",placeholder="For example, 12,450.25")
        answer=st.text_area("Your reasoning and recommendation",height=130,max_chars=12000,placeholder="What did you find? Explain your method, cite the value, and recommend a next step.")
        submitted=st.form_submit_button("Check my analysis",type="primary",icon=":material/check_circle:")
    if submitted:
        try:
            if not segment or len(answer.strip())<20:
                raise ValueError("Select a segment and add at least 20 characters of reasoning.")
            numeric=float(value.replace(",","").strip())
            result=check_answer(task,segment,numeric)
            report=f"Segment: {segment}\nValue: {numeric}\n{answer}"
            st.session_state["result_"+task["id"]]=(result,report)
            save_result(task,report,result)
        except ValueError as exc:
            st.warning(str(exc) if "convert" not in str(exc) else "Enter a numeric value, with optional commas and decimal places.")
    stored=st.session_state.get("result_"+task["id"])
    if stored:
        result,answer_text=stored
        render_result(task,result,answer_text)
        if current_user() and storage.is_unlocked(task["id"]):
            if st.button("Get AI coaching on my reasoning",key="coach_"+task["id"],disabled=not bool(setting("OPENAI_API_KEY"))):
                try:
                    with st.spinner("Reviewing your analysis against the full dataset…"):
                        review=review_answer({**task,"reference":result["answer"]},df,answer_text)
                    st.session_state["coaching_"+task["id"]]=review
                except (RuntimeError,ValueError) as exc: st.warning(str(exc))
            if st.session_state.get("coaching_"+task["id"]):
                coach=st.session_state["coaching_"+task["id"]]
                st.info(coach["summary"])
                for item in coach["improvements"]: st.write("• "+item)
                st.caption("Coaching does not change your numerical check score or award extra XP.")

def practice():
    heading("Learn / Practice lab","Small questions. Stronger instincts.","Explore the evidence, test your conclusion, and build your analytical confidence.")
    industry,df=active_data()
    tasks=build_challenges(df,industry)
    choice=st.radio("Choose a challenge",range(len(tasks)),format_func=lambda i:tasks[i]["title"],horizontal=True)
    workbench(tasks[choice],df)

def daily():
    heading("Learn / Daily challenge","One day. One new insight.","Daily briefs refresh at midnight UTC. Your best result counts once per brief.")
    industry=st.selectbox("Daily challenge industry",list(CATALOG))
    df=load_dataset(industry)
    workbench(daily_challenge(df,industry),df)
