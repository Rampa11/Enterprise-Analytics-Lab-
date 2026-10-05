-- Run once in the Supabase SQL editor before enabling account persistence.
-- Additive: existing analytics and legacy profile tables are retained.
begin;
create table if not exists public.lab_profiles (
 user_id uuid primary key references auth.users(id) on delete cascade,
 display_name text not null,
 plan text not null default 'free' check(plan in ('free','premium')),
 credits integer not null default 0 check(credits>=0),
 premium_until timestamptz,
 stripe_customer_id text,
 stripe_subscription_id text,
 billing_version bigint not null default 0
);
create table if not exists public.lab_attempts (
 user_id uuid not null references auth.users(id) on delete cascade,
 challenge_id text not null,
 title text not null,
 industry text not null,
 kind text not null check(kind in ('practice','daily','manager')),
 dataset_id text not null,
 score integer not null check(score between 0 and 100),
 xp integer not null check(xp between 0 and 150),
 answer text not null check(length(answer)<=13000),
 result jsonb not null,
 completed_at timestamptz not null default now(),
 primary key(user_id,challenge_id)
);
create index if not exists lab_attempts_completed on public.lab_attempts(user_id,completed_at desc);
create table if not exists public.lab_unlocks (
 user_id uuid not null references auth.users(id) on delete cascade,
 challenge_id text not null,
 created_at timestamptz not null default now(),
 primary key(user_id,challenge_id)
);
create table if not exists public.lab_billing_events (
 event_key text primary key,
 created_at timestamptz not null default now()
);
alter table public.lab_profiles enable row level security;
alter table public.lab_attempts enable row level security;
alter table public.lab_unlocks enable row level security;
alter table public.lab_billing_events enable row level security;
revoke all on public.lab_profiles,public.lab_attempts,public.lab_unlocks,public.lab_billing_events from anon,authenticated;
grant select on public.lab_profiles,public.lab_unlocks to authenticated;
grant all on public.lab_profiles,public.lab_attempts,public.lab_unlocks,public.lab_billing_events to service_role;
drop policy if exists lab_own_profile on public.lab_profiles;
create policy lab_own_profile on public.lab_profiles for select to authenticated using ((select auth.uid())=user_id);
drop policy if exists lab_own_unlocks on public.lab_unlocks;
create policy lab_own_unlocks on public.lab_unlocks for select to authenticated using ((select auth.uid())=user_id);
-- Scores, answers, entitlements, and billing events are written only by the app server.
-- Full answer JSON is deliberately not exposed through the public Data API.

create or replace function public.lab_save_attempt(p_user_id uuid,p_record jsonb)
returns boolean language plpgsql security invoker set search_path='' as $$
declare n integer;
begin
 insert into public.lab_attempts(user_id,challenge_id,title,industry,kind,dataset_id,score,xp,answer,result,completed_at)
 values(p_user_id,p_record->>'challenge_id',p_record->>'title',p_record->>'industry',p_record->>'kind',p_record->>'dataset_id',
 (p_record->>'score')::integer,(p_record->>'xp')::integer,p_record->>'answer',p_record->'result',now())
 on conflict(user_id,challenge_id) do update set score=excluded.score,xp=excluded.xp,answer=excluded.answer,result=excluded.result,completed_at=excluded.completed_at
 where excluded.score>public.lab_attempts.score;
 get diagnostics n=row_count;
 return n>0;
end $$;

create or replace function public.lab_unlock_answer(p_user_id uuid,p_challenge_id text)
returns boolean language plpgsql security invoker set search_path='' as $$
declare p public.lab_profiles;
begin
 select * into p from public.lab_profiles where user_id=p_user_id for update;
 if not found then return false; end if;
 if exists(select 1 from public.lab_unlocks where user_id=p_user_id and challenge_id=p_challenge_id) then return true; end if;
 if p.plan='premium' and (p.premium_until is null or p.premium_until>now()) then return true; end if;
 if p.credits<1 or not exists(select 1 from public.lab_attempts where user_id=p_user_id and challenge_id=p_challenge_id) then return false; end if;
 insert into public.lab_unlocks(user_id,challenge_id) values(p_user_id,p_challenge_id);
 update public.lab_profiles set credits=credits-1 where user_id=p_user_id;
 return true;
end $$;

create or replace function public.lab_apply_billing(p_event_key text,p_user_id uuid,p_credits integer,p_plan text,p_until timestamptz,p_customer text,p_subscription text,p_version bigint)
returns boolean language plpgsql security invoker set search_path='' as $$
declare n integer;
begin
 if p_credits not in (0,2) or (p_plan is not null and p_plan not in ('free','premium')) then raise exception 'Invalid billing update'; end if;
 -- Profile lock serializes credit updates and subscription events.
 perform 1 from public.lab_profiles where user_id=p_user_id for update;
 if not found then raise exception 'Profile not found'; end if;
 insert into public.lab_billing_events(event_key) values(p_event_key) on conflict do nothing;
 get diagnostics n=row_count;
 if n=0 then return false; end if;
 update public.lab_profiles set credits=credits+p_credits,stripe_customer_id=coalesce(p_customer,stripe_customer_id) where user_id=p_user_id;
 if p_plan is not null then
   update public.lab_profiles set plan=p_plan,premium_until=p_until,stripe_subscription_id=p_subscription,billing_version=p_version
   where user_id=p_user_id and billing_version<=p_version;
 end if;
 return true;
end $$;

create or replace function public.lab_leaderboard()
returns table(display_name text,total_xp bigint,completed bigint,average_score numeric)
language sql stable security invoker set search_path='' as $$
 select p.display_name,sum(a.xp),count(*),round(avg(a.score),1)
 from public.lab_profiles p join public.lab_attempts a on a.user_id=p.user_id
 group by p.user_id,p.display_name order by sum(a.xp) desc,avg(a.score) desc,p.display_name limit 50
$$;
revoke all on function public.lab_save_attempt(uuid,jsonb) from public,anon,authenticated;
revoke all on function public.lab_unlock_answer(uuid,text) from public,anon,authenticated;
revoke all on function public.lab_apply_billing(text,uuid,integer,text,timestamptz,text,text,bigint) from public,anon,authenticated;
revoke all on function public.lab_leaderboard() from public,anon,authenticated;
grant execute on function public.lab_save_attempt(uuid,jsonb) to service_role;
grant execute on function public.lab_unlock_answer(uuid,text) to service_role;
grant execute on function public.lab_apply_billing(text,uuid,integer,text,timestamptz,text,text,bigint) to service_role;
grant execute on function public.lab_leaderboard() to service_role;

create table if not exists public.lab_ai_usage (
 user_id uuid not null references auth.users(id) on delete cascade,
 day date not null,
 calls integer not null default 0,
 primary key(user_id,day)
);
alter table public.lab_ai_usage enable row level security;
revoke all on public.lab_ai_usage from anon,authenticated;
grant all on public.lab_ai_usage to service_role;
create or replace function public.lab_reserve_ai_call(p_user_id uuid)
returns boolean language plpgsql security invoker set search_path='' as $$
declare allowance integer; n integer; today date := (now() at time zone 'UTC')::date;
begin
 select case when plan='premium' and (premium_until is null or premium_until>now()) then 100 else 5 end
 into allowance from public.lab_profiles where user_id=p_user_id;
 if not found then return false; end if;
 insert into public.lab_ai_usage(user_id,day,calls) values(p_user_id,today,1)
 on conflict(user_id,day) do update set calls=public.lab_ai_usage.calls+1
 where public.lab_ai_usage.calls<allowance;
 get diagnostics n=row_count;
 return n>0;
end $$;
revoke all on function public.lab_reserve_ai_call(uuid) from public,anon,authenticated;
grant execute on function public.lab_reserve_ai_call(uuid) to service_role;

commit;
