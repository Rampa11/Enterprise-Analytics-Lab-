import html
import streamlit as st
from auth import current_user
from lab.config import ROOT
from lab.storage import profile
from lab.datasets import CATALOG, load_dataset, label, aggregate, dictionary

STYLE = """
<style>
.stApp{background:#f5f7f9}
.block-container{max-width:1320px;padding-top:4.5rem;padding-bottom:3rem}
h1,h2,h3{letter-spacing:-.035em;color:#172c3e}
h1{font-size:2.5rem!important;font-weight:750!important}
h2{font-size:1.6rem!important}h3{font-size:1.15rem!important}
[data-testid="stSidebar"]{background:#112938;border-right:1px solid #233c4d}
[data-testid="stSidebar"] p,[data-testid="stSidebar"] h3,[data-testid="stSidebar"] small,[data-testid="stSidebarNav"] span{color:#dce7eb!important}
[data-testid="stSidebarNav"] a:hover{background:#203f50}
[data-testid="stSidebarNav"] a[aria-current="page"]{background:#244c56;border-left:3px solid #6ad2bd}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p{color:#9fb6c4!important}
[data-testid="stMetric"]{padding:19px 22px;border:1px solid #e1e8ed;border-radius:12px;background:white}
[data-testid="stMetricValue"]{color:#173c48;font-weight:700}
[data-testid="stMetricLabel"]{color:#637987}
[data-testid="stVerticalBlockBorderWrapper"]{border-radius:12px}
[data-testid="stBaseButton-primary"],[data-testid="stBaseButton-secondary"]{border-radius:8px}
.eyebrow{font-size:11px;font-weight:750;text-transform:uppercase;letter-spacing:.16em;color:#63818f;margin:0 0 8px}
.brand{padding:8px 0 20px;color:#f5fcff;font-size:18px;font-weight:750;letter-spacing:-.03em}
.brand-mark{display:inline-flex;align-items:center;justify-content:center;width:34px;height:34px;border-radius:9px;background:#72d7be;color:#113e3b;margin-right:8px;font-weight:900}
.brand small{display:block;color:#94b0bf;margin:4px 0 0 46px;font-size:10px;letter-spacing:.17em}
.hero{display:grid;grid-template-columns:1.5fr 1fr;gap:28px;padding:34px 38px;background:#e5f2ee;border:1px solid #cde3db;border-radius:16px;margin:14px 0 24px}
.hero h2{font-size:2.5rem!important;line-height:1.12;margin:10px 0 16px;color:#153f3d}
.hero p{color:#4b6b68;font-size:15px;line-height:1.65;max-width:530px}
.pill{display:inline-block;padding:5px 10px;border-radius:20px;background:white;color:#32756b;font-size:11px;font-weight:700;letter-spacing:.05em}
.hero-chart{background:white;border:1px solid #d5e5df;border-radius:12px;padding:20px 22px;box-shadow:0 12px 30px #315c4c0b}
.hero-chart p{font-size:11px;margin:0}
.chart-bars{height:110px;display:flex;align-items:end;gap:16px;margin:18px 0 8px;border-bottom:1px solid #dde9e4}
.chart-bar{flex:1;background:#87c8b8;border-radius:5px 5px 0 0;min-height:5px}
.chart-bar:last-child{background:#1b8172}
.chart-labels{display:flex;justify-content:space-around;color:#738b83;font-size:10px}
.step{font-size:11px;color:#0c8473;font-weight:750;letter-spacing:.1em}
.footer{border-top:1px solid #e0e7eb;padding-top:18px;margin-top:35px;color:#7b8c97;font-size:11px;letter-spacing:.05em}
@media(max-width:760px){.hero{grid-template-columns:1fr;padding:24px}.hero h2{font-size:2rem!important}.hero-chart{display:none}.block-container{padding:4.5rem 1rem 2rem}h1{font-size:2rem!important}}
</style>
"""
def apply_style():
    st.markdown(STYLE,unsafe_allow_html=True)

def heading(kicker,title,subtitle):
    st.markdown(f'<div class="eyebrow">{html.escape(kicker)}</div>',unsafe_allow_html=True)
    st.title(title)
    st.caption(subtitle)

def sidebar():
    st.logo(str(ROOT / "assets" / "brand.svg"), size="large", icon_image=str(ROOT / "assets" / "mark.svg"))
    with st.sidebar:
        st.caption("YOUR ANALYST WORKSPACE")
        account=current_user()
        if account:
            st.write(account.get("name","Analyst"))
            p=profile()
            st.caption(f"{p['plan'].capitalize()} plan · {p['credits']} answer credits")
        else:
            st.caption("Guest session · explore at your pace")

def footer():
    st.markdown('<div class="footer">ENTERPRISE ANALYTICS LAB / LEARN BY SOLVING. BUILD WITH EVIDENCE.</div>',unsafe_allow_html=True)

def active_data():
    st.session_state.setdefault("industry","Oil & Gas")
    industry=st.selectbox("Practice industry",list(CATALOG),key="industry")
    generated=st.session_state.get("active_generated")
    if generated and generated["industry"]==industry:
        st.caption("Using your generated dataset")
        if st.button("Use the original industry dataset",key="reset_dataset"):
            del st.session_state["active_generated"]
            st.rerun()
        return industry,generated["df"]
    return industry,load_dataset(industry)

def explorer(df,industry,key="explorer"):
    st.caption(f"{len(df):,} observations · {len(df.columns)} columns · synthetic training data")
    data_tab,chart_tab,dictionary_tab=st.tabs(["Dataset","Explore a chart","Data dictionary"])
    with data_tab:
        group=CATALOG[industry]["group"]
        selected=st.multiselect(f"Filter {group}",sorted(df[group].astype(str).unique()),key=key+"_filter")
        filtered=df[df[group].astype(str).isin(selected)] if selected else df
        st.dataframe(filtered,hide_index=True,width="stretch",height=300)
        st.caption(f"Showing {len(filtered):,} of {len(df):,} rows. Challenges use the complete dataset.")
        st.download_button("Download complete CSV",df.to_csv(index=False).encode(),"analytics_dataset.csv","text/csv",key=key+"_download",icon=":material/download:")
    with chart_tab:
        cols=st.columns(2)
        measures=[c for c in df.select_dtypes(include="number").columns if not c.endswith("_id")]
        metric=cols[0].selectbox("Measure",measures,key=key+"_measure")
        op=cols[1].selectbox("Calculation",["sum","mean","max","min"],key=key+"_op")
        st.bar_chart(aggregate(df,CATALOG[industry]["group"],metric,op),color="#118674",height=260)
        st.caption(f"{label(metric)} · {op} by {CATALOG[industry]['group']} · all rows")
    with dictionary_tab:
        st.dataframe(dictionary(df),hide_index=True,width="stretch")
        st.caption("Synthetic data supports descriptive analysis. It does not establish causes or represent real people.")
