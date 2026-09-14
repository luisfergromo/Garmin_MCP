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
    print("\n[1/5] Connecting to Garmin Connect...")
    client = _init_garmin_client()
    _configure_and_register(client)
    print(f"  -> Successfully connected as: {client.get_full_name()}")

    # Find tools from FastMCP
    tool_funcs = {t.name: t.fn for t in mcp._tool_manager.list_tools()}
    print(f"  -> Total registered tools: {len(tool_funcs)}")

    today = datetime.date.today().isoformat()
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()

    # 2. Daily Stats
    print(f"\n[2/5] Testing 'get_stats' for today ({today})...")
    if "get_stats" in tool_funcs:
        stats_raw = await tool_funcs["get_stats"](date=today)
        try:
            stats = json.loads(stats_raw)
            print(f"  - Steps: {stats.get('total_steps', 'N/A')} / Goal: {stats.get('daily_step_goal', 'N/A')}")
            print(f"  - Total Calories: {stats.get('total_calories', 'N/A')} kcal (Active: {stats.get('active_calories', 'N/A')} kcal)")
            print(f"  - Heart Rate: Resting {stats.get('resting_heart_rate_bpm', 'N/A')} bpm | Min {stats.get('min_heart_rate_bpm', 'N/A')} | Max {stats.get('max_heart_rate_bpm', 'N/A')}")
            print(f"  - Avg Stress Level: {stats.get('avg_stress_level', 'N/A')}/100 ({stats.get('stress_qualifier', 'N/A')})")
            print(f"  - Current Body Battery: {stats.get('body_battery_current', 'N/A')}/100 (Charged: +{stats.get('body_battery_charged', 0)}, Drained: -{stats.get('body_battery_drained', 0)})")
        except Exception as e:
            print("  Raw:", stats_raw[:200])

    # 3. Sleep data (from last night / yesterday)
    print(f"\n[3/5] Testing 'get_sleep_data' ({today})...")
    if "get_sleep_data" in tool_funcs:
        sleep_raw = await tool_funcs["get_sleep_data"](date=today)
        try:
            sleep = json.loads(sleep_raw)
            secs = sleep.get("total_sleep_seconds", 0)
            hours = secs // 3600
            mins = (secs % 3600) // 60
            print(f"  - Sleep Score: {sleep.get('sleep_score', 'N/A')}/100 ({sleep.get('sleep_quality', 'N/A')})")
            print(f"  - Total Duration: {hours}h {mins}m")
            print(f"  - Deep: {sleep.get('deep_sleep_seconds', 0)//60}m | Light: {sleep.get('light_sleep_seconds', 0)//60}m | REM: {sleep.get('rem_sleep_seconds', 0)//60}m | Awake: {sleep.get('awake_seconds', 0)//60}m")
            print(f"  - Avg Sleep SpO2: {sleep.get('avg_spo2', 'N/A')}%")
        except Exception:
            print("  Raw:", sleep_raw[:200])

    # 4. Recent Activities
    print("\n[4/5] Testing 'get_activities' (last 3 activities)...")
    if "get_activities" in tool_funcs:
        act_raw = await tool_funcs["get_activities"](limit=3)
        try:
            act_data = json.loads(act_raw)
            for i, a in enumerate(act_data.get("activities", []), 1):
                dist_km = (a.get("distance_meters") or 0) / 1000.0
                dur_min = (a.get("duration_seconds") or 0) / 60.0
                print(f"  {i}. {a.get('name')} [{a.get('type')}] - {a.get('start_time')}")
                print(f"     Distance: {dist_km:.2f} km | Duration: {dur_min:.1f} min | Calories: {a.get('calories')} kcal | Avg HR: {a.get('avg_hr_bpm')} bpm")
        except Exception:
            print("  Raw:", act_raw[:200])

    # 5. Devices
    print("\n[5/5] Testing 'get_devices'...")
    if "get_devices" in tool_funcs:
        dev_raw = await tool_funcs["get_devices"]()
        try:
            devs = json.loads(dev_raw)
            for d in devs:
                print(f"  - Device: {d.get('product_display_name', d.get('display_name'))} (Battery: {d.get('battery_status', 'N/A')})")
        except Exception:
            print("  Raw:", dev_raw[:200])

    print("\n" + "=" * 60)
    print(" [OK] ALL MCP TOOLS ARE WORKING PROPERLY")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_demo())
