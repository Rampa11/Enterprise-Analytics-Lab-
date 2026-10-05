from datetime import datetime, timezone
import hashlib
import math
from lab.datasets import CATALOG, aggregate, fingerprint, label

def build_challenges(df, industry):
    spec = CATALOG[industry]
    group, metric, risk = spec["group"], spec["metric"], spec["risk"]
    dataset_id = fingerprint(df)
    configs = [
        ("Find the strongest performer",metric,"sum","Foundation","Compare total output across business segments."),
        ("Look beyond the totals",metric,"mean","Intermediate","Compare average performance per observation, rather than scale alone."),
        ("Investigate the pressure point",risk,"mean","Intermediate","Identify where the highest average value deserves a closer look.")]
    tasks = []
    for idx,(title,value,op,difficulty,brief) in enumerate(configs):
        grouped = aggregate(df,group,value,op)
        best = float(grouped.max())
        winners = grouped[grouped == best].index.astype(str).tolist()
        question = f"Which {group} has the highest {'total' if op == 'sum' else 'average'} {label(value).lower()}? Report the value and recommend one next step."
        tasks.append(dict(id=hashlib.sha256(f"{industry}:{dataset_id}:{idx}".encode()).hexdigest()[:24],title=title,question=question,brief=brief,difficulty=difficulty,group=group,metric=value,operation=op,expected=best,winners=winners,options=sorted(df[group].astype(str).unique().tolist()),industry=industry,dataset_id=dataset_id,kind="practice"))
    return tasks

def daily_challenge(df, industry, day=None):
    day = day or datetime.now(timezone.utc).date()
    tasks = build_challenges(df,industry)
    task = tasks[day.toordinal()%len(tasks)].copy()
    task.update(id=f"daily:{day.isoformat()}:{task['id']}",kind="daily",title=f"Daily brief · {day.strftime('%d %b')}",day=day.isoformat())
    return task

def check_answer(task, segment, value):
    if not math.isfinite(value):
        raise ValueError("Enter a finite numeric value.")
    segment_ok = segment in task["winners"]
    value_ok = math.isclose(value,task["expected"],rel_tol=.005,abs_tol=.01)
    return dict(score=(50 if segment_ok else 0)+(50 if value_ok else 0),segment_correct=segment_ok,value_correct=value_ok,
        feedback="Both checks passed." if segment_ok and value_ok else "Review the segment and aggregation, then try again.",
        method=f"Group by {task['group']}, calculate {task['operation']}({task['metric']}), and sort descending.",
        answer=f"{', '.join(task['winners'])}: {task['expected']:,.4f}",source="Computed answer check")
