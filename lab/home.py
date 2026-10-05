import html
import pandas as pd
import streamlit as st
from auth import current_user
from lab import storage
from lab.datasets import CATALOG,load_dataset,aggregate
from lab.ui import heading

def home():
    heading("Your learning workspace","Make your next insight count.","Real business questions. Hands-on analysis. A little progress, every day.")
    rows=storage.history()
    stats=storage.stats(rows)
    grouped=aggregate(load_dataset("Oil & Gas"),"region","production_barrels").sort_index()
    bars="".join(f'<div class="chart-bar" style="height:{v/grouped.max()*100:.0f}%"></div>' for v in grouped)
    labels="".join(f"<span>{html.escape(str(x))}</span>" for x in grouped.index)
    st.markdown(f"""<section class="hero"><div><span class="pill">YOUR NEXT CHAPTER STARTS HERE</span><h2>Think like an analyst.<br>Learn by doing.</h2><p>Step into a business, explore its data, and turn a question into a decision. Your first case is ready when you are.</p><span class="step">01 EXPLORE → 02 ANALYZE → 03 IMPROVE</span></div><div class="hero-chart"><p>INSIDE THE LAB / OIL &amp; GAS</p><h3>Where is production strongest?</h3><div class="chart-bars">{bars}</div><div class="chart-labels">{labels}</div><p style="margin-top:16px">Production by region · actual training dataset</p></div></section>""",unsafe_allow_html=True)
    a,b,_=st.columns([1,1,2])
    a.page_link("pages/Practice_Lab.py",label="Open practice lab",icon=":material/arrow_forward:")
    b.page_link("pages/Industry_Selection.py",label="Explore industries",icon=":material/grid_view:")
    st.write("")
    for col,(name,value) in zip(st.columns(4),[("Challenges completed",stats["completed"]),("Experience earned",f"{stats['xp']:,} XP"),("Average score",f"{stats['average']}%" if rows else "—"),("Current streak",f"{stats['streak']} days")]):
        col.metric(name,value)
    if not current_user():
        st.caption("Guest progress lasts for this browser session. Sign in to save future work to your account.")
    st.write("")
    left,right=st.columns([1.6,1])
    with left:
        st.subheader("Choose your next move")
        for number,title,desc,page,icon in [
            ("01","Build your foundations","Short, focused questions with checks against the complete dataset.","pages/Practice_Lab.py",":material/science:"),
            ("02","Take the manager's brief","Turn findings into a clear business recommendation.","pages/AI_Business_Manager.py",":material/work:"),
            ("03","Keep your momentum","A fresh daily challenge, with progress that counts.","pages/Daily_Challenge.py",":material/today:")]:
            with st.container(border=True):
                st.markdown(f'<span class="step">{number} / LEARNING PATH</span>',unsafe_allow_html=True)
                st.subheader(title)
                st.caption(desc)
                st.page_link(page,label="Start here",icon=icon)
    with right:
        with st.container(border=True):
            st.markdown('<span class="step">YOUR DEVELOPMENT</span>',unsafe_allow_html=True)
            st.subheader(f"Level {stats['level']} · Analyst in progress")
            st.progress(stats["level_progress"])
            st.caption(f"{stats['xp']%500} / 500 XP toward your next level")
            st.write("A good analysis answers three things:")
            st.markdown("1. What does the data show?\n2. Why does it matter?\n3. What should happen next?")
            st.page_link("pages/Profile.py",label="View your progress",icon=":material/trending_up:")
        with st.container(border=True):
            st.subheader("A dataset of your own")
            st.caption("Create reproducible industry data, download it, and bring it into the lab.")
            st.page_link("pages/AI_Dataset_Generator.py",label="Open dataset studio",icon=":material/table_chart:")

def industries():
    heading("Explore / Industry library","Pick a world to work in.","Five industries. Different decisions. The same evidence-first mindset.")
    for offset in range(0,len(CATALOG),3):
        for col,(name,spec) in zip(st.columns(3),list(CATALOG.items())[offset:offset+3]):
            with col,st.container(border=True):
                st.markdown(spec["icon"])
                st.subheader(name)
                st.write(spec["description"])
                df=load_dataset(name)
                st.caption(f"{len(df):,} observations · {len(df.columns)} fields · 3 core challenges")
                if st.button("Practice in "+name,key="choose_"+name,width="stretch"):
                    st.session_state["industry"]=name
                    st.session_state.pop("active_generated",None)
                    st.switch_page("pages/Practice_Lab.py")
    st.info("Every case includes a downloadable dataset, a data dictionary, and a chart explorer.",icon=":material/lightbulb:")

def progress():
    from lab.learning import render_result
    heading("Your growth / Progress","Every insight adds up.","Review your best attempts, see what is improving, and keep your work.")
    rows=storage.history()
    s=storage.stats(rows)
    for col,(name,value) in zip(st.columns(4),[("Completed",s["completed"]),("Total XP",s["xp"]),("Average score",s["average"]),("Streak",f"{s['streak']} days")]):
        col.metric(name,value)
    st.subheader("Your achievements")
    for col,(name,description,earned) in zip(st.columns(5),storage.badges(rows)):
        with col,st.container(border=True):
            st.write(":material/verified:" if earned else ":material/lock:")
            st.write("**"+name+"**")
            st.caption(description)
    st.subheader("Analysis history")
    if not rows:
        st.info("Complete a practice challenge to start your history.")
        st.page_link("pages/Practice_Lab.py",label="Start a challenge",icon=":material/arrow_forward:")
        return
    frame=pd.DataFrame(rows)
    columns=["title","industry","kind","score","xp","completed_at"]
    st.dataframe(frame[columns],hide_index=True,width="stretch")
    st.download_button("Export progress CSV",frame[columns].to_csv(index=False),"learning_progress.csv","text/csv")
    selected=st.selectbox("Review a completed challenge",range(len(rows)),format_func=lambda i:rows[i]["title"]+" · "+rows[i]["industry"])
    record=rows[selected]
    st.write(record["answer"])
    task={"id":record["challenge_id"],"question":record["title"],"industry":record["industry"]}
    render_result(task,record["result"],record["answer"],saved=True)

def rankings():
    heading("Community / Leaderboard","Learn together. Grow together.","Ranked by XP from distinct challenges. Repeat attempts improve your best result.")
    rows=storage.leaderboard()
    if rows:
        table=pd.DataFrame(rows).rename(columns={"display_name":"Analyst","total_xp":"XP","completed":"Challenges","average_score":"Average score"})
        table.insert(0,"Rank",range(1,len(table)+1))
        st.dataframe(table,hide_index=True,width="stretch")
    else:
        st.info("No rankings are available yet. Complete a challenge after signing in to start building your record.")
    st.caption("Public rankings use an assigned analyst alias, never your email. Guest results are not published.")
