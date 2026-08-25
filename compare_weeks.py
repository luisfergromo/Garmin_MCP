import sys
import datetime
import json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from garmin_mcp import _init_garmin_client

client = _init_garmin_client()

# Fetch recent 50 activities
acts = client.get_activities(0, 50)

# Define periods:
# 1. Rolling 7 days:
#    Period A (Current 7 days): 19-Aug-2026 to 25-Aug-2026
#    Period B (Previous 7 days): 12-Aug-2026 to 18-Aug-2026
# 2. Calendar weeks (Mon-Sun):
#    Week 34 (17-23 Aug)
#    Week 35 (24-30 Aug, in progress)

p_current = []
p_previous = []

d_today = datetime.date(2026, 8, 25)
d_7_ago = d_today - datetime.timedelta(days=6)    # 2026-08-20 to 2026-08-25 (or 19-25)
d_14_ago = d_today - datetime.timedelta(days=13)  # 2026-08-13 to 2026-08-19

for a in acts:
    dt_str = a.get("startTimeLocal", "")[:10]
    if not dt_str:
        continue
    dt = datetime.date.fromisoformat(dt_str)
    
    if datetime.date(2026, 8, 19) <= dt <= datetime.date(2026, 8, 25):
        p_current.append(a)
    elif datetime.date(2026, 8, 12) <= dt <= datetime.date(2026, 8, 18):
        p_previous.append(a)

def analyze_period(name, act_list):
    total_dur_min = sum(a.get("duration", 0) for a in act_list) / 60.0
    total_cal = sum(a.get("calories", 0) for a in act_list)
    total_load = sum(a.get("activityTrainingLoad", 0) or 0 for a in act_list)
    
    by_sport = {}
    for a in act_list:
        sport = a.get("activityType", {}).get("typeKey", "other")
        dist = a.get("distance", 0) / 1000.0
        dur = a.get("duration", 0) / 60.0
        load = a.get("activityTrainingLoad", 0) or 0
        
        if sport not in by_sport:
            by_sport[sport] = {"count": 0, "dist_km": 0, "dur_min": 0, "load": 0}
        by_sport[sport]["count"] += 1
        by_sport[sport]["dist_km"] += dist
        by_sport[sport]["dur_min"] += dur
        by_sport[sport]["load"] += load

    return {
        "name": name,
        "count": len(act_list),
        "total_load": round(total_load, 1),
        "total_dur_min": round(total_dur_min, 1),
        "total_dur_hrs": round(total_dur_min / 60.0, 2),
        "total_cal": round(total_cal, 0),
        "by_sport": by_sport,
        "activities": act_list
    }

res_curr = analyze_period("Últimos 7 días (19 - 25 Ago)", p_current)
res_prev = analyze_period("Semana previa (12 - 18 Ago)", p_previous)

print(json.dumps({"current": res_curr, "previous": res_prev}, indent=2, default=str))
