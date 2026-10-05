import hashlib
import streamlit as st
from lab.ai import manager_brief,review_answer
from auth import current_user
from lab.challenges import build_challenges
from lab.config import setting
from lab.datasets import CATALOG,generate_dataset,fingerprint
from lab.ui import heading,active_data,explorer
from lab.learning import save_result,render_result

def manager():
    heading("Learn / Business manager","You've got the brief.","Move from finding a number to making a business recommendation.")
    industry,df=active_data()
    role=st.selectbox("Your manager",["Operations manager","Finance manager","Product manager"])
    core=build_challenges(df,industry)
    default={"title":f"{industry}: performance review","situation":f"Your {role.lower()} needs an evidence-based review before the next planning meeting.","tasks":[t["question"] for t in core],"deliverable":"Write a concise report with three findings, supporting figures, a prioritized recommendation, and one limitation."}
    brief_key=f"brief:{industry}:{fingerprint(df)}:{role}"
    if st.button("Generate a fresh AI brief",icon=":material/auto_awesome:",disabled=not bool(setting("OPENAI_API_KEY") and current_user())):
        try:
            with st.spinner("Preparing your brief…"): st.session_state[brief_key]=manager_brief(df,industry,role)
        except RuntimeError as exc: st.warning(str(exc))
    brief=st.session_state.get(brief_key,default)
    question=brief["situation"]+"\n"+"\n".join(brief["tasks"])+"\n"+brief["deliverable"]
    task=dict(id="manager:"+hashlib.sha256((brief_key+question).encode()).hexdigest()[:24],title=brief["title"],question=question,industry=industry,kind="manager",dataset_id=fingerprint(df))
    with st.container(border=True):
        st.caption(role.upper()+" / PROJECT BRIEF")
        st.subheader(brief["title"])
        st.write(brief["situation"])
        for idx,item in enumerate(brief["tasks"],1): st.write(f"**{idx:02d}.** {item}")
        st.info(brief["deliverable"])
    with st.expander("Open the dataset",expanded=False): explorer(df,industry,key="manager_data")
    st.caption("Rubric: accuracy 40% · reasoning 30% · recommendations 20% · clarity 10%")
    with st.form("report_"+task["id"]):
        report=st.text_area("Your business report",height=240,max_chars=12000,placeholder="Executive summary\n\nKey findings and evidence\n\nRecommendation\n\nLimitations")
        submit=st.form_submit_button("Submit for review",type="primary")
    if not current_user():
        st.info("Sign in for AI-generated briefs and report reviews. You can still draft and download a report as a guest.")
    if not setting("OPENAI_API_KEY"):
        st.info("You can draft and download your report. AI review will be available when coaching is connected; no score or XP is awarded without a review.")
    if submit:
        try:
            with st.spinner("Reviewing your report…"): result=review_answer(task,df,report)
            st.session_state["result_"+task["id"]]=(result,report)
            save_result(task,report,result)
        except (RuntimeError,ValueError) as exc: st.warning(str(exc))
    st.download_button("Download report draft",report or "",file_name="business_report.txt",mime="text/plain")
    if st.session_state.get("result_"+task["id"]):
        result,answer=st.session_state["result_"+task["id"]]
        render_result(task,result,answer)

def studio():
    heading("Tools / Dataset studio","Create your next case study.","Reproducible synthetic data with sensible relationships, ready for your analysis.")
    with st.container(border=True):
        a,b,c=st.columns([2,1,1])
        industry=a.selectbox("Industry",list(CATALOG),key="studio_industry")
        rows=b.number_input("Observations",min_value=100,max_value=10000,value=1000,step=100)
        seed=c.number_input("Dataset seed",min_value=0,max_value=999999,value=42)
        st.caption("The same settings produce the same dataset. Revenue, delays, and quality measures follow explicit business rules.")
        if st.button("Generate dataset",type="primary",icon=":material/add_chart:"):
            st.session_state["studio_dataset"]={"industry":industry,"df":generate_dataset(industry,int(rows),int(seed)),"seed":seed}
    generated=st.session_state.get("studio_dataset")
    if generated:
        st.subheader(f"Your {generated['industry']} dataset")
        explorer(generated["df"],generated["industry"],key="studio")
        if st.button("Use this dataset in the practice lab",type="primary",icon=":material/arrow_forward:"):
            st.session_state["active_generated"]=generated
            st.session_state["industry"]=generated["industry"]
            st.switch_page("pages/Practice_Lab.py")
    else:
        st.info("Choose an industry and generate your first dataset. Your preview and download will appear here.")
