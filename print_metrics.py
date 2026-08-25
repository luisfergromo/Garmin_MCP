import sys
import datetime
import json
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from garmin_mcp import _init_garmin_client

client = _init_garmin_client()
today = datetime.date.today().isoformat()

print("--- TRAINING STATUS ---")
try:
    ts = client.get_training_status(today)
    print(json.dumps(ts, indent=2))
except Exception as e:
    print("TS err:", e)

print("--- MAX METRICS & VO2 MAX ---")
try:
    mm = client.get_max_metrics(today)
    print(json.dumps(mm, indent=2))
except Exception as e:
    print("MM err:", e)

print("--- TRAINING READINESS ---")
try:
    tr = client.get_training_readiness(today)
    print(json.dumps(tr, indent=2))
except Exception as e:
    print("TR err:", e)

print("--- HRV DATA ---")
try:
    hrv = client.get_hrv_data(today)
    print(json.dumps(hrv, indent=2))
except Exception as e:
    print("HRV err:", e)

print("--- ENDURANCE & HILL SCORE ---")
try:
    print("Endurance:", client.get_endurance_score(today))
except Exception as e:
    print("Endurance err:", e)

try:
    print("Hill:", client.get_hill_score(today))
except Exception as e:
    print("Hill err:", e)

print("--- RECENT ACTIVITIES SUMMARY ---")
try:
    acts = client.get_activities(0, 7)
    for a in acts:
        print(f"- {a.get('startTimeLocal')}: {a.get('activityName')} | {a.get('activityType', {}).get('typeKey')} | Dist: {a.get('distance', 0)/1000:.2f}km | Dur: {a.get('duration', 0)/60:.1f}min | FC Avg: {a.get('averageHR')} | TE Aerobic: {a.get('aerobicTrainingEffect')} | Load: {a.get('activityTrainingLoad')}")
except Exception as e:
    print("Acts err:", e)
