"""
Health & Wellness Data functions for Garmin Connect MCP Server
"""
import json
from typing import Optional

# The garmin_client will be set by the main file
garmin_client = None


def configure(client):
    """Configure the module with the Garmin client instance"""
    global garmin_client
    garmin_client = client


def register_tools(app):
    """Register all health and wellness tools with the MCP server app"""

    @app.tool()
    async def get_stats(date: str) -> str:
        """Get daily activity stats with curated essential metrics.

        Returns a summary of daily health and activity data including steps,
        calories, heart rate, stress, body battery, and sleep metrics.

        Args:
            date: Date in YYYY-MM-DD format
        """
        try:
            stats = garmin_client.get_stats(date)
            if not stats:
                return f"No stats found for {date}"

            summary = {
                "date": stats.get('calendarDate'),
                # Activity
                "total_steps": stats.get('totalSteps'),
                "daily_step_goal": stats.get('dailyStepGoal'),
                "distance_meters": stats.get('totalDistanceMeters'),
                "floors_ascended": round(stats.get('floorsAscended', 0), 1) if stats.get('floorsAscended') else None,
                "floors_descended": round(stats.get('floorsDescended', 0), 1) if stats.get('floorsDescended') else None,
                # Calories
                "total_calories": stats.get('totalKilocalories'),
                "active_calories": stats.get('activeKilocalories'),
                "bmr_calories": stats.get('bmrKilocalories'),
                # Activity duration
                "highly_active_seconds": stats.get('highlyActiveSeconds'),
                "active_seconds": stats.get('activeSeconds'),
                "sedentary_seconds": stats.get('sedentarySeconds'),
                "sleeping_seconds": stats.get('sleepingSeconds'),
                # Intensity minutes
                "moderate_intensity_minutes": stats.get('moderateIntensityMinutes'),
                "vigorous_intensity_minutes": stats.get('vigorousIntensityMinutes'),
                "intensity_minutes_goal": stats.get('intensityMinutesGoal'),
                # Heart rate
                "min_heart_rate_bpm": stats.get('minHeartRate'),
                "max_heart_rate_bpm": stats.get('maxHeartRate'),
                "resting_heart_rate_bpm": stats.get('restingHeartRate'),
                "last_7_days_avg_resting_hr": stats.get('lastSevenDaysAvgRestingHeartRate'),
                # Stress
                "avg_stress_level": stats.get('averageStressLevel'),
                "max_stress_level": stats.get('maxStressLevel'),
                "stress_qualifier": stats.get('stressQualifier'),
                # Body Battery
                "body_battery_charged": stats.get('bodyBatteryChargedValue'),
                "body_battery_drained": stats.get('bodyBatteryDrainedValue'),
                "body_battery_highest": stats.get('bodyBatteryHighestValue'),
                "body_battery_lowest": stats.get('bodyBatteryLowestValue'),
                "body_battery_current": stats.get('bodyBatteryMostRecentValue'),
                # SpO2
                "avg_spo2_percent": stats.get('averageSpo2'),
                "lowest_spo2_percent": stats.get('lowestSpo2'),
                # Respiration
                "avg_waking_respiration": stats.get('avgWakingRespirationValue'),
                "highest_respiration": stats.get('highestRespirationValue'),
                "lowest_respiration": stats.get('lowestRespirationValue'),
            }
            summary = {k: v for k, v in summary.items() if v is not None}
            return json.dumps(summary, indent=2)
        except Exception as e:
            return f"Error retrieving stats: {str(e)}"

    @app.tool()
    async def get_user_summary(date: str) -> str:
        """Get user summary data for a specific date.

        Args:
            date: Date in YYYY-MM-DD format
        """
        try:
            summary = garmin_client.get_user_summary(date)
            if not summary:
                return f"No user summary found for {date}"
            return json.dumps(summary, indent=2)
        except Exception as e:
            return f"Error retrieving user summary: {str(e)}"

    @app.tool()
    async def get_body_composition(start_date: str, end_date: str = None) -> str:
        """Get body composition data for a single date or date range.

        Args:
            start_date: Date in YYYY-MM-DD format or start date if end_date provided
            end_date: Optional end date in YYYY-MM-DD format for date range
        """
        try:
            if end_date:
                composition = garmin_client.get_body_composition(start_date, end_date)
                if not composition:
                    return f"No body composition data found between {start_date} and {end_date}"
            else:
                composition = garmin_client.get_body_composition(start_date)
                if not composition:
                    return f"No body composition data found for {start_date}"
            return json.dumps(composition, indent=2)
        except Exception as e:
            return f"Error retrieving body composition data: {str(e)}"

    @app.tool()
    async def get_heart_rates(date: str) -> str:
        """Get heart rate data for a specific date.

        Args:
            date: Date in YYYY-MM-DD format
        """
        try:
            hr_data = garmin_client.get_heart_rates(date)
            if not hr_data:
                return f"No heart rate data found for {date}"
            return json.dumps(hr_data, indent=2)
        except Exception as e:
            return f"Error retrieving heart rate data: {str(e)}"

    @app.tool()
    async def get_sleep_data(date: str) -> str:
        """Get detailed sleep data for a specific date.

        Returns sleep stages, duration, scores, and quality metrics.

        Args:
            date: Date in YYYY-MM-DD format
        """
        try:
            sleep = garmin_client.get_sleep_data(date)
            if not sleep:
                return f"No sleep data found for {date}"

            daily_sleep = sleep.get('dailySleepDTO', {})
            curated = {
                "date": date,
                "sleep_start": daily_sleep.get('sleepStartTimestampLocal'),
                "sleep_end": daily_sleep.get('sleepEndTimestampLocal'),
                "total_sleep_seconds": daily_sleep.get('sleepTimeSeconds'),
                "deep_sleep_seconds": daily_sleep.get('deepSleepSeconds'),
                "light_sleep_seconds": daily_sleep.get('lightSleepSeconds'),
                "rem_sleep_seconds": daily_sleep.get('remSleepSeconds'),
                "awake_seconds": daily_sleep.get('awakeSleepSeconds'),
                "sleep_score": daily_sleep.get('sleepScores', {}).get('overallScore'),
                "sleep_quality": daily_sleep.get('sleepScores', {}).get('qualityScore'),
                "recovery_score": daily_sleep.get('sleepScores', {}).get('recoveryScore'),
                "restlessness_score": daily_sleep.get('sleepScores', {}).get('restlessnessScore'),
                "avg_spo2": daily_sleep.get('averageSpO2Value'),
                "avg_respiration": daily_sleep.get('averageRespirationValue'),
                "avg_stress": daily_sleep.get('averageStress'),
            }
            curated = {k: v for k, v in curated.items() if v is not None}
            return json.dumps(curated, indent=2)
        except Exception as e:
            return f"Error retrieving sleep data: {str(e)}"

    @app.tool()
    async def get_stress_data(date: str) -> str:
        """Get detailed stress data for a specific date.

        Args:
            date: Date in YYYY-MM-DD format
        """
        try:
            stress = garmin_client.get_stress_data(date)
            if not stress:
                return f"No stress data found for {date}"
            return json.dumps(stress, indent=2)
        except Exception as e:
            return f"Error retrieving stress data: {str(e)}"

    @app.tool()
    async def get_steps_data(date: str) -> str:
        """Get step count data for a specific date.

        Args:
            date: Date in YYYY-MM-DD format
        """
        try:
            steps = garmin_client.get_steps_data(date)
            if not steps:
                return f"No step data found for {date}"
            return json.dumps(steps, indent=2)
        except Exception as e:
            return f"Error retrieving step data: {str(e)}"

    @app.tool()
    async def get_spo2_data(date: str) -> str:
        """Get SpO2 (blood oxygen saturation) data for a specific date.

        Args:
            date: Date in YYYY-MM-DD format
        """
        try:
            spo2 = garmin_client.get_spo2_data(date)
            if not spo2:
                return f"No SpO2 data found for {date}"
            return json.dumps(spo2, indent=2)
        except Exception as e:
            return f"Error retrieving SpO2 data: {str(e)}"

    @app.tool()
    async def get_respiration_data(date: str) -> str:
        """Get respiration rate data for a specific date.

        Args:
            date: Date in YYYY-MM-DD format
        """
        try:
            resp = garmin_client.get_respiration_data(date)
            if not resp:
                return f"No respiration data found for {date}"
            return json.dumps(resp, indent=2)
        except Exception as e:
            return f"Error retrieving respiration data: {str(e)}"

    @app.tool()
    async def get_rhr_day(date: str) -> str:
        """Get resting heart rate for a specific date.

        Args:
            date: Date in YYYY-MM-DD format
        """
        try:
            rhr = garmin_client.get_rhr_day(date)
            if not rhr:
                return f"No resting heart rate data found for {date}"
            return json.dumps(rhr, indent=2)
        except Exception as e:
            return f"Error retrieving resting heart rate: {str(e)}"

    @app.tool()
    async def get_hrv_data(date: str) -> str:
        """Get heart rate variability (HRV) data for a specific date.

        Args:
            date: Date in YYYY-MM-DD format
        """
        try:
            hrv = garmin_client.get_hrv_data(date)
            if not hrv:
                return f"No HRV data found for {date}"
            return json.dumps(hrv, indent=2)
        except Exception as e:
            return f"Error retrieving HRV data: {str(e)}"

    @app.tool()
    async def get_body_battery(date: str) -> str:
        """Get Body Battery data for a specific date.

        Body Battery measures your body's energy reserves throughout the day.

        Args:
            date: Date in YYYY-MM-DD format
        """
        try:
            bb = garmin_client.get_body_battery(date)
            if not bb:
                return f"No Body Battery data found for {date}"
            return json.dumps(bb, indent=2)
        except Exception as e:
            return f"Error retrieving Body Battery data: {str(e)}"

    @app.tool()
    async def get_blood_pressure(start_date: str, end_date: str = None) -> str:
        """Get blood pressure measurements.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: Optional end date in YYYY-MM-DD format
        """
        try:
            if end_date:
                bp = garmin_client.get_blood_pressure(start_date, end_date)
            else:
                bp = garmin_client.get_blood_pressure(start_date)
            if not bp:
                return f"No blood pressure data found for {start_date}"
            return json.dumps(bp, indent=2)
        except Exception as e:
            return f"Error retrieving blood pressure data: {str(e)}"

    @app.tool()
    async def get_hydration_data(date: str) -> str:
        """Get hydration tracking data for a specific date.

        Args:
            date: Date in YYYY-MM-DD format
        """
        try:
            hydration = garmin_client.get_hydration_data(date)
            if not hydration:
                return f"No hydration data found for {date}"
            return json.dumps(hydration, indent=2)
        except Exception as e:
            return f"Error retrieving hydration data: {str(e)}"
