"""Optional local-only PostgreSQL integration check. Every change is rolled back."""
import json
import os
from pathlib import Path
from uuid import uuid4
import psycopg2
from dotenv import dotenv_values

def run():
    source=os.environ.get("LAB_DB_ENV")
    if not source:
        raise RuntimeError("Set LAB_DB_ENV to a local database env file.")
    env=dotenv_values(source)
    if env["DB_HOST"] not in ("localhost","127.0.0.1"):
        raise RuntimeError("This check runs only against a local PostgreSQL server.")
    conn=psycopg2.connect(connect_timeout=5,host=env["DB_HOST"],port=env.get("DB_PORT",5432),dbname=env["DB_NAME"],user=env["DB_USER"],password=env["DB_PASSWORD"])
    cur=conn.cursor()
    try:
        cur.execute("select to_regclass('public.lab_profiles'),to_regclass('auth.users')")
        existing=cur.fetchone()
        if any(existing):
            raise RuntimeError("Use a local database without lab_profiles or auth.users for this isolated check.")
        cur.execute("create schema if not exists auth")
        cur.execute("create table auth.users(id uuid primary key)")
        cur.execute("create function auth.uid() returns uuid language sql stable as $$select nullif(current_setting('request.jwt.claim.sub',true),'')::uuid$$")
        for role in ("anon","authenticated","service_role"):
            cur.execute("select 1 from pg_roles where rolname=%s",(role,))
            if not cur.fetchone(): cur.execute(f"create role {role} nologin")
        cur.execute("alter role service_role bypassrls")
        sql=(Path(__file__).resolve().parents[1]/"sql/platform_setup.sql").read_text(encoding="utf-8")
        sql=sql.replace("begin;","",1).rsplit("commit;",1)[0]
        cur.execute(sql)
        cur.execute("grant usage on schema public,auth to anon,authenticated,service_role")
        user,other=str(uuid4()),str(uuid4())
        cur.execute("insert into auth.users values(%s),(%s)",(user,other))
        cur.execute("insert into public.lab_profiles(user_id,display_name,credits) values(%s,'A',2),(%s,'B',0)",(user,other))
        cur.execute("set local role service_role")
        record=dict(challenge_id="test",title="Test",industry="Oil & Gas",kind="practice",dataset_id="data",score=50,xp=50,answer="Report",result={"score":50})
        cur.execute("select public.lab_save_attempt(%s,%s::jsonb)",(user,json.dumps(record)))
        assert cur.fetchone()[0]
        cur.execute("select public.lab_save_attempt(%s,%s::jsonb)",(user,json.dumps(record)))
        assert not cur.fetchone()[0]
        record.update(score=100,xp=100,result={"score":100})
        cur.execute("select public.lab_save_attempt(%s,%s::jsonb)",(user,json.dumps(record)))
        assert cur.fetchone()[0]
        cur.execute("select count(*),sum(xp) from public.lab_attempts where user_id=%s",(user,))
        assert cur.fetchone()==(1,100)
        for _ in range(2):
            cur.execute("select public.lab_unlock_answer(%s,'test')",(user,))
            assert cur.fetchone()[0]
        cur.execute("select credits from public.lab_profiles where user_id=%s",(user,))
        assert cur.fetchone()[0]==1
        for _ in range(2):
            cur.execute("select public.lab_apply_billing('checkout:one',%s,2,null,null,null,null,1)",(user,))
        cur.execute("select credits from public.lab_profiles where user_id=%s",(user,))
        assert cur.fetchone()[0]==3
        cur.execute("select public.lab_apply_billing('active',%s,0,'premium',now()+interval '1 day',null,'sub',20)",(user,))
        cur.execute("select public.lab_apply_billing('stale',%s,0,'free',null,null,'sub',10)",(user,))
        cur.execute("select plan from public.lab_profiles where user_id=%s",(user,))
        assert cur.fetchone()[0]=="premium"
        for _ in range(5):
            cur.execute("select public.lab_reserve_ai_call(%s)",(other,))
            assert cur.fetchone()[0]
        cur.execute("select public.lab_reserve_ai_call(%s)",(other,))
        assert not cur.fetchone()[0]
        cur.execute("reset role")
        cur.execute("set local role authenticated")
        cur.execute("select set_config('request.jwt.claim.sub',%s,true)",(user,))
        cur.execute("select user_id from public.lab_profiles")
        assert [str(r[0]) for r in cur.fetchall()]==[user]
        for statement in ["select * from public.lab_attempts","update public.lab_profiles set credits=999","select public.lab_leaderboard()"]:
            cur.execute("savepoint denied")
            try:
                cur.execute(statement)
            except psycopg2.errors.InsufficientPrivilege:
                cur.execute("rollback to savepoint denied")
            else:
                raise AssertionError("Unauthorized access was allowed")
        print("PASS: best-score persistence, duplicate XP prevention, permanent unlocks, billing deduplication, stale event protection, AI limits, RLS, and forbidden mutations.")
    finally:
        conn.rollback()
        conn.close()
        print("All database test changes rolled back.")

if __name__=="__main__":
    run()
