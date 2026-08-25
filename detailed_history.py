import sys
import datetime
import json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from garmin_mcp import _init_garmin_client

client = _init_garmin_client()

# Fetch 100 activities
acts = client.get_activities(0, 100)

print(f"Total actividades recuperadas: {len(acts)}\n")

# Print all August activities
print("--- HISTORIAL DE AGOSTO 2026 ---")
for a in acts:
    dt_str = a.get("startTimeLocal", "")
    if not dt_str or not dt_str.startswith("2026-08"):
        continue
    
    date_obj = datetime.date.fromisoformat(dt_str[:10])
    weekday = date_obj.strftime("%A") # Monday, Tuesday, etc.
    name = a.get("activityName")
    type_key = a.get("activityType", {}).get("typeKey")
    dur = round(a.get("duration", 0) / 60.0, 1)
    dist = round(a.get("distance", 0) / 1000.0, 2)
    load = round(a.get("activityTrainingLoad", 0) or 0, 1)
    cal = a.get("calories")
    hr = a.get("averageHR")
    
    print(f"{dt_str[:10]} ({weekday:9s}) | {name:22s} | {type_key:18s} | {dist:5.2f} km | {dur:5.1f} min | FC: {str(hr):4s} | Load: {load:5.1f}")

# Group strictly by Lunes a Viernes:
# Semana Actual: Lunes 24 Ago - Viernes 28 Ago (hasta hoy Martes 25)
# Semana Pasada: Lunes 17 Ago - Viernes 21 Ago
# Semana Antepasada: Lunes 10 Ago - Viernes 14 Ago

def summarize_week(title, start_d, end_d):
    print(f"\n=======================================================")
    print(f" {title} ({start_d.isoformat()} a {end_d.isoformat()})")
    print(f"=======================================================")
    
    week_acts = []
    for a in acts:
        dt_str = a.get("startTimeLocal", "")[:10]
        if not dt_str:
            continue
        d = datetime.date.fromisoformat(dt_str)
        if start_d <= d <= end_d:
            week_acts.append(a)
    
    total_load = sum(a.get("activityTrainingLoad", 0) or 0 for a in week_acts)
    total_dur = sum(a.get("duration", 0) for a in week_acts) / 60.0
    total_cal = sum(a.get("calories", 0) for a in week_acts)
    
    by_sport = {}
    for a in week_acts:
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

    print(f"Total Actividades: {len(week_acts)}")
    print(f"Carga Total (Training Load): {total_load:.1f} pts")
    print(f"Tiempo Total: {total_dur:.1f} min ({total_dur/60:.2f} hrs)")
    print(f"Calorías: {total_cal} kcal")
    print("\nDesglose por disciplina:")
    for sp, data in by_sport.items():
        print(f"  - {sp:18s}: {data['count']} sesion(es) | {data['dist_km']:.2f} km | {data['dur_min']:.1f} min | Carga: {data['load']:.1f}")
    
    print("\nDetalle de sesiones:")
    for a in week_acts:
        dt_str = a.get("startTimeLocal", "")
        print(f"  * {dt_str}: {a.get('activityName')} [{a.get('activityType', {}).get('typeKey')}] | {a.get('distance', 0)/1000:.2f} km | {a.get('duration', 0)/60:.1f} m | FC {a.get('averageHR')} | Load {a.get('activityTrainingLoad')}")

summarize_week("ESTA SEMANA (Lunes - Viernes en curso)", datetime.date(2026, 8, 24), datetime.date(2026, 8, 28))
summarize_week("SEMANA PASADA (Lunes - Viernes)", datetime.date(2026, 8, 17), datetime.date(2026, 8, 21))
summarize_week("SEMANA ANTEPASADA (Lunes - Viernes)", datetime.date(2026, 8, 10), datetime.date(2026, 8, 14))
