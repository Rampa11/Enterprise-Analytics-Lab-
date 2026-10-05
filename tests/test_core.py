from datetime import date,timedelta
import json
from types import SimpleNamespace
import numpy as np
import pandas as pd
import pytest
from pydantic import ValidationError
from lab.datasets import CATALOG,load_dataset,generate_dataset,evidence,fingerprint
from lab.challenges import build_challenges,check_answer,daily_challenge
from lab import storage
from lab.ai import Review,review_answer

@pytest.mark.parametrize("industry",list(CATALOG))
def test_challenges_match_complete_dataset(industry):
    df=load_dataset(industry)
    for task in build_challenges(df,industry):
        expected=df.groupby(task["group"])[task["metric"]].agg(task["operation"])
        assert task["expected"]==pytest.approx(expected.max())
        assert check_answer(task,task["winners"][0],task["expected"])["score"]==100
        other=next(x for x in task["options"] if x not in task["winners"])
        assert check_answer(task,other,task["expected"]*2+1)["score"]==0

def test_ties_and_invalid_numbers():
    df=pd.DataFrame({"region":["North","South"],"production_barrels":[100,100],"downtime_hours":[1,2]})
    task=build_challenges(df,"Oil & Gas")[0]
    assert set(task["winners"])=={"North","South"}
    for bad in [float("nan"),float("inf"),float("-inf")]:
        with pytest.raises(ValueError): check_answer(task,"North",bad)

def test_full_data_context_not_preview():
    df=pd.DataFrame({"region":["North"]*5+["South"],"production_barrels":[1]*5+[1000],"downtime_hours":[1]*6})
    payload=json.loads(evidence(df,"Oil & Gas"))
    assert payload["rows"]==6
    assert payload["group_totals"]["production_barrels"]["South"]==1000
    assert build_challenges(df,"Oil & Gas")[0]["winners"]==["South"]

@pytest.mark.parametrize("industry",list(CATALOG))
def test_generator_reproducible_and_challenge_ready(industry):
    a=generate_dataset(industry,100,42)
    pd.testing.assert_frame_equal(a,generate_dataset(industry,100,42))
    assert fingerprint(a)!=fingerprint(generate_dataset(industry,100,43))
    assert len(a)==100 and not a.isna().any().any()
    assert len(build_challenges(a,industry))==3
    json.loads(evidence(a,industry))

def test_business_relationships():
    food=generate_dataset("Food & Beverage")
    np.testing.assert_allclose(food.revenue,food.units_sold*food.unit_price)
    logistics=generate_dataset("Logistics")
    assert (logistics.delayed_shipments<=logistics.shipments_per_day).all()
    factory=generate_dataset("Manufacturing")
    assert factory.defect_rate.between(0,1).all()
    np.testing.assert_array_equal(factory.defective_units,np.rint(factory.units_produced*factory.defect_rate))

def test_daily_stability_and_dataset_identity():
    df=load_dataset("Oil & Gas")
    today=date(2026,10,5)
    assert daily_challenge(df,"Oil & Gas",today)==daily_challenge(df,"Oil & Gas",today)
    assert daily_challenge(df,"Oil & Gas",today)["id"]!=daily_challenge(df,"Oil & Gas",today+timedelta(days=1))["id"]
    assert build_challenges(df,"Oil & Gas")[0]["id"]!=build_challenges(generate_dataset("Oil & Gas"),"Oil & Gas")[0]["id"]

def test_guest_best_score_prevents_xp_farming(monkeypatch):
    monkeypatch.setattr(storage.st,"session_state",{})
    monkeypatch.setattr(storage,"current_user",lambda:None)
    task=build_challenges(load_dataset("Oil & Gas"),"Oil & Gas")[0]
    assert storage.save_attempt(task,"report",{"score":50})
    assert not storage.save_attempt(task,"retry",{"score":50})
    assert not storage.save_attempt(task,"worse",{"score":0})
    assert storage.save_attempt(task,"better",{"score":100})
    assert len(storage.history())==1
    assert storage.stats(storage.history())["xp"]==100
    with pytest.raises(ValueError): storage.save_attempt(task,"report",{"score":None})

def test_streaks_are_deduplicated_and_expire():
    today=date(2026,10,5)
    def r(day): return dict(completed_at=day.isoformat()+"T12:00:00+00:00",score=80,xp=80)
    rows=[r(today),r(today),r(today-timedelta(days=1)),r(today-timedelta(days=2))]
    assert storage.stats(rows,today)["streak"]==3
    assert storage.stats(rows,today+timedelta(days=1))["streak"]==3
    assert storage.stats(rows,today+timedelta(days=2))["streak"]==0

def test_ai_failure_never_returns_invented_score():
    df=load_dataset("Oil & Gas")
    task=build_challenges(df,"Oil & Gas")[0]
    with pytest.raises(RuntimeError,match="not configured"):
        review_answer(task,df,"A sufficiently long report with a recommendation and evidence.")
    for score in [-1,101,"70",True]:
        with pytest.raises(ValidationError):
            Review(score=score,summary="x",strengths=[],improvements=[],suggested_approach="x")

def test_generated_bounds():
    with pytest.raises(ValueError): generate_dataset("Oil & Gas",1)
    with pytest.raises(ValueError): generate_dataset("Unknown",1000)
