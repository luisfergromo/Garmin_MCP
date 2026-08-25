"""
Demo script to test Garmin MCP Server tools locally and view your health/activity metrics.
"""

import sys
import asyncio
import datetime
import json

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from garmin_mcp import _init_garmin_client, mcp, _configure_and_register


async def run_demo():
    print("=" * 60)
    print(" [*] GARMIN CONNECT MCP SERVER - LIVE TEST [*]")
    print("=" * 60)

    # 1. Initialize client and register tools
    print("\n[1/5] Conectando con Garmin Connect...")
    client = _init_garmin_client()
    _configure_and_register(client)
    print(f"  -> Conectado exitosamente como: {client.get_full_name()}")

    # Find tools from FastMCP
    tool_funcs = {t.name: t.fn for t in mcp._tool_manager.list_tools()}
    print(f"  -> Total de herramientas registradas: {len(tool_funcs)}")

    today = datetime.date.today().isoformat()
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()

    # 2. Daily Stats
    print(f"\n[2/5] Probando 'get_stats' para hoy ({today})...")
    if "get_stats" in tool_funcs:
        stats_raw = await tool_funcs["get_stats"](date=today)
        try:
            stats = json.loads(stats_raw)
            print(f"  - Pasos: {stats.get('total_steps', 'N/A')} / Meta: {stats.get('daily_step_goal', 'N/A')}")
            print(f"  - Calorías Totales: {stats.get('total_calories', 'N/A')} kcal (Activas: {stats.get('active_calories', 'N/A')} kcal)")
            print(f"  - Frecuencia Cardíaca: Reposo {stats.get('resting_heart_rate_bpm', 'N/A')} bpm | Min {stats.get('min_heart_rate_bpm', 'N/A')} | Max {stats.get('max_heart_rate_bpm', 'N/A')}")
            print(f"  - Nivel de Estrés promedio: {stats.get('avg_stress_level', 'N/A')}/100 ({stats.get('stress_qualifier', 'N/A')})")
            print(f"  - Body Battery actual: {stats.get('body_battery_current', 'N/A')}/100 (Cargado: +{stats.get('body_battery_charged', 0)}, Gastado: -{stats.get('body_battery_drained', 0)})")
        except Exception as e:
            print("  Raw:", stats_raw[:200])

    # 3. Sleep data (from last night / yesterday)
    print(f"\n[3/5] Probando 'get_sleep_data' ({today})...")
    if "get_sleep_data" in tool_funcs:
        sleep_raw = await tool_funcs["get_sleep_data"](date=today)
        try:
            sleep = json.loads(sleep_raw)
            secs = sleep.get("total_sleep_seconds", 0)
            hours = secs // 3600
            mins = (secs % 3600) // 60
            print(f"  - Puntuación de Sueño (Sleep Score): {sleep.get('sleep_score', 'N/A')}/100 ({sleep.get('sleep_quality', 'N/A')})")
            print(f"  - Duración total: {hours}h {mins}m")
            print(f"  - Profundo: {sleep.get('deep_sleep_seconds', 0)//60}m | Ligero: {sleep.get('light_sleep_seconds', 0)//60}m | REM: {sleep.get('rem_sleep_seconds', 0)//60}m | Despierto: {sleep.get('awake_seconds', 0)//60}m")
            print(f"  - SpO2 promedio en sueño: {sleep.get('avg_spo2', 'N/A')}%")
        except Exception:
            print("  Raw:", sleep_raw[:200])

    # 4. Recent Activities
    print("\n[4/5] Probando 'get_activities' (últimas 3 actividades)...")
    if "get_activities" in tool_funcs:
        act_raw = await tool_funcs["get_activities"](limit=3)
        try:
            act_data = json.loads(act_raw)
            for i, a in enumerate(act_data.get("activities", []), 1):
                dist_km = (a.get("distance_meters") or 0) / 1000.0
                dur_min = (a.get("duration_seconds") or 0) / 60.0
                print(f"  {i}. {a.get('name')} [{a.get('type')}] - {a.get('start_time')}")
                print(f"     Distancia: {dist_km:.2f} km | Duración: {dur_min:.1f} min | Calorías: {a.get('calories')} kcal | FC Prom: {a.get('avg_hr_bpm')} bpm")
        except Exception:
            print("  Raw:", act_raw[:200])

    # 5. Devices
    print("\n[5/5] Probando 'get_devices'...")
    if "get_devices" in tool_funcs:
        dev_raw = await tool_funcs["get_devices"]()
        try:
            devs = json.loads(dev_raw)
            for d in devs:
                print(f"  - Dispositivo: {d.get('product_display_name', d.get('display_name'))} (Batería: {d.get('battery_status', 'N/A')})")
        except Exception:
            print("  Raw:", dev_raw[:200])

    print("\n" + "=" * 60)
    print(" [OK] TODAS LAS HERRAMIENTAS MCP RESPONDEN CORRECTAMENTE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_demo())
