from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest
from lab.datasets import load_dataset
from lab.challenges import build_challenges

ROOT=Path(__file__).resolve().parents[1]

def start():
    app=AppTest.from_file(str(ROOT/"dashboard.py"),default_timeout=90).run()
    assert not app.exception
    return app

@pytest.mark.parametrize("page",["Industry_Selection","Practice_Lab","AI_Business_Manager","Daily_Challenge","AI_Dataset_Generator","Profile","Leaderboard","Login","Pricing"])
def test_every_page_renders_without_credentials(page):
    app=start().switch_page(f"pages/{page}.py").run()
    assert not app.exception

def test_guest_submission_daily_and_progress():
    app=start().switch_page("pages/Practice_Lab.py").run()
    task=build_challenges(load_dataset("Oil & Gas"),"Oil & Gas")[0]
    next(x for x in app.selectbox if x.label=="Your leading segment").select(task["winners"][0])
    next(x for x in app.text_input if x.label=="Your calculated value").input(str(task["expected"]))
    app.text_area[0].input("I grouped all observations by region and summed production. I recommend reviewing capacity in the leading region.")
    next(x for x in app.button if x.label=="Check my analysis").click().run()
    assert not app.exception
    assert len(app.session_state["guest_history"])==1
    assert app.session_state["guest_history"][0]["score"]==100
    next(x for x in app.button if x.label=="Check my analysis").click().run()
    assert len(app.session_state["guest_history"])==1
    app.switch_page("pages/Profile.py").run()
    assert not app.exception
    assert any("100" in str(x.value) for x in app.metric)
    app.switch_page("pages/Daily_Challenge.py").run()
    assert not app.exception
    from lab.challenges import daily_challenge
    task=daily_challenge(load_dataset("Oil & Gas"),"Oil & Gas")
    next(x for x in app.selectbox if x.label=="Your leading segment").select(task["winners"][0])
    next(x for x in app.text_input if x.label=="Your calculated value").input(str(task["expected"]))
    app.text_area[0].input("I used the complete dataset and the requested aggregation. My next step is to compare operational capacity.")
    next(x for x in app.button if x.label=="Check my analysis").click().run()
    assert not app.exception
    assert len(app.session_state["guest_history"])==2
    assert any(r["kind"]=="daily" for r in app.session_state["guest_history"])

def test_generator_stays_available_and_routes_to_practice():
    app=start().switch_page("pages/AI_Dataset_Generator.py").run()
    next(x for x in app.button if x.label=="Generate dataset").click().run()
    assert not app.exception
    assert len(app.session_state["studio_dataset"]["df"])==1000
    app.run()
    assert len(app.session_state["studio_dataset"]["df"])==1000
    next(x for x in app.button if x.label=="Use this dataset in the practice lab").click().run()
    assert not app.exception
    assert len(app.session_state["active_generated"]["df"])==1000

def test_bad_number_does_not_save_score():
    app=start().switch_page("pages/Practice_Lab.py").run()
    next(x for x in app.selectbox if x.label=="Your leading segment").select("North")
    next(x for x in app.text_input if x.label=="Your calculated value").input("NaN")
    app.text_area[0].input("A report containing enough text to pass the reasoning-length validation.")
    next(x for x in app.button if x.label=="Check my analysis").click().run()
    assert not app.exception
    assert app.warning
    assert "guest_history" not in app.session_state or not app.session_state["guest_history"]

def test_payment_query_cannot_grant_access():
    app=AppTest.from_file(str(ROOT/"dashboard.py"),default_timeout=90)
    app.query_params["payment_success"]="premium"
    app.run()
    assert not app.exception
    assert "account" not in app.session_state
    assert "plan" not in app.session_state
