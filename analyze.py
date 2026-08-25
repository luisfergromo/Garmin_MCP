import sys
import datetime
import json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from garmin_mcp import _init_garmin_client

client = _init_garmin_client()
today = datetime.date.today().isoformat()

report = {}

# 1. User summary & stats
try:
    report["stats"] = client.get_stats(today)
except Exception as e:
    report["stats_err"] = str(e)

# 2. Training status & readiness
try:
    report["training_status"] = client.get_training_status(today)
except Exception as e:
    report["training_status_err"] = str(e)

try:
    report["training_readiness"] = client.get_training_readiness(today)
except Exception as e:
    report["training_readiness_err"] = str(e)

# 3. VO2 Max / Fitness metrics
try:
    report["max_metrics"] = client.get_max_metrics(today)
except Exception as e:
    report["max_metrics_err"] = str(e)

# 4. HRV
try:
    report["hrv"] = client.get_hrv_data(today)
except Exception as e:
    report["hrv_err"] = str(e)

# 5. Sleep
try:
    report["sleep"] = client.get_sleep_data(today)
except Exception as e:
    report["sleep_err"] = str(e)

# 6. Race predictions
try:
    report["race_predictions"] = client.get_race_predictions()
except Exception as e:
    report["race_predictions_err"] = str(e)

# 7. Endurance & Hill scores
try:
    report["endurance_score"] = client.get_endurance_score(today)
except Exception as e:
    report["endurance_score_err"] = str(e)

try:
    report["hill_score"] = client.get_hill_score(today)
except Exception as e:
    report["hill_score_err"] = str(e)

# 8. Activities list (last 10)
try:
    report["activities"] = client.get_activities(0, 10)
except Exception as e:
    report["activities_err"] = str(e)

with open("full_analysis.json", "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, default=str)

print("DATA_FETCHED_SUCCESSFULLY")
