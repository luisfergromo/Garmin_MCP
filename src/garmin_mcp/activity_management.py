"""
Activity Management functions for Garmin Connect MCP Server
"""
import json
from typing import Any, Dict, Optional

# The garmin_client will be set by the main file
garmin_client = None


def configure(client):
    """Configure the module with the Garmin client instance"""
    global garmin_client
    garmin_client = client


def register_tools(app):
    """Register all activity management tools with the MCP server app"""

    @app.tool()
    async def get_activities_by_date(
        start_date: str,
        end_date: str,
        activity_type: str = "",
        page: int = 0,
        page_size: int = 100,
    ) -> str:
        """Get activities between specified dates with pagination support.

        Activities are ordered newest-first. Use page/page_size for large histories.
        When has_more is true, pass next_page as page to get the next batch.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            activity_type: Optional activity type filter (e.g., cycling, running, swimming)
            page: Zero-based page number (default 0)
            page_size: Number of activities per page, max 200 (default 100)
        """
        try:
            page_size = min(max(1, page_size), 200)
            start = page * page_size

            params: Dict[str, Any] = {
                "startDate": start_date,
                "endDate": end_date,
                "start": str(start),
                "limit": str(page_size),
            }
            if activity_type:
                params["activityType"] = activity_type

            activities = garmin_client.connectapi(
                garmin_client.garmin_connect_activities,
                params=params,
            )

            if not activities:
                return json.dumps({
                    "count": 0,
                    "page": page,
                    "page_size": page_size,
                    "has_more": False,
                    "date_range": {"start": start_date, "end": end_date},
                    "activities": [],
                }, indent=2)

            has_more = len(activities) == page_size
            curated: Dict[str, Any] = {
                "count": len(activities),
                "page": page,
                "page_size": page_size,
                "has_more": has_more,
                "date_range": {"start": start_date, "end": end_date},
                "activities": [],
            }
            if has_more:
                curated["next_page"] = page + 1

            for a in activities:
                activity = {
                    "id": a.get('activityId'),
                    "name": a.get('activityName'),
                    "type": a.get('activityType', {}).get('typeKey'),
                    "event_type": (a.get('eventType') or {}).get('typeKey'),
                    "start_time": a.get('startTimeLocal'),
                    "distance_meters": a.get('distance'),
                    "duration_seconds": a.get('duration'),
                    "calories": a.get('calories'),
                    "avg_hr_bpm": a.get('averageHR'),
                    "max_hr_bpm": a.get('maxHR'),
                    "steps": a.get('steps'),
                    "elevation_gain_meters": a.get('elevationGain'),
                    "elevation_loss_meters": a.get('elevationLoss'),
                }
                activity = {k: v for k, v in activity.items() if v is not None}
                curated["activities"].append(activity)

            return json.dumps(curated, indent=2)
        except Exception as e:
            return f"Error retrieving activities by date: {str(e)}"

    @app.tool()
    async def get_activities_fordate(date: str) -> str:
        """Get activities for a specific date

        Args:
            date: Date in YYYY-MM-DD format
        """
        try:
            data = garmin_client.get_activities_fordate(date)
            if not data:
                return f"No activities found for {date}"

            activities_data = data.get('ActivitiesForDay', {})
            payload = activities_data.get('payload', [])

            if not payload:
                return f"No activities found for {date}"

            curated = {
                "date": date,
                "count": len(payload),
                "activities": []
            }

            for a in payload:
                activity = {
                    "id": a.get('activityId'),
                    "name": a.get('activityName'),
                    "type": a.get('activityType', {}).get('typeKey'),
                    "event_type": (a.get('eventType') or {}).get('typeKey'),
                    "start_time": a.get('startTimeLocal'),
                    "distance_meters": a.get('distance'),
                    "duration_seconds": a.get('duration'),
                    "calories": a.get('calories'),
                    "avg_hr_bpm": a.get('averageHR'),
                    "max_hr_bpm": a.get('maxHR'),
                }
                activity = {k: v for k, v in activity.items() if v is not None}
                curated["activities"].append(activity)

            return json.dumps(curated, indent=2)
        except Exception as e:
            return f"Error retrieving activities for date: {str(e)}"

    @app.tool()
    async def get_activities(limit: int = 20, start: int = 0) -> str:
        """Get recent activities with pagination.

        Args:
            limit: Number of activities to retrieve (default 20, max 100)
            start: Offset for pagination (default 0)
        """
        try:
            limit = min(max(1, limit), 100)
            activities = garmin_client.get_activities(start, limit)
            if not activities:
                return "No recent activities found"

            curated = {
                "count": len(activities),
                "start": start,
                "limit": limit,
                "activities": []
            }

            for a in activities:
                activity = {
                    "id": a.get('activityId'),
                    "name": a.get('activityName'),
                    "type": a.get('activityType', {}).get('typeKey'),
                    "event_type": (a.get('eventType') or {}).get('typeKey'),
                    "start_time": a.get('startTimeLocal'),
                    "distance_meters": a.get('distance'),
                    "duration_seconds": a.get('duration'),
                    "calories": a.get('calories'),
                    "avg_hr_bpm": a.get('averageHR'),
                    "max_hr_bpm": a.get('maxHR'),
                    "steps": a.get('steps'),
                    "elevation_gain_meters": a.get('elevationGain'),
                }
                activity = {k: v for k, v in activity.items() if v is not None}
                curated["activities"].append(activity)

            return json.dumps(curated, indent=2)
        except Exception as e:
            return f"Error retrieving activities: {str(e)}"

    @app.tool()
    async def get_activity(activity_id: int) -> str:
        """Get detailed information about a specific activity.

        Args:
            activity_id: The activity ID to retrieve
        """
        try:
            activity = garmin_client.get_activity(activity_id)
            if not activity:
                return f"No activity found with ID {activity_id}"

            summary = activity.get('summaryDTO', {})
            curated = {
                "id": activity.get('activityId'),
                "name": activity.get('activityName'),
                "type": activity.get('activityType', {}).get('typeKey'),
                "event_type": (activity.get('eventType') or {}).get('typeKey'),
                "description": activity.get('description'),
                "start_time": summary.get('startTimeLocal'),
                "distance_meters": summary.get('distance'),
                "duration_seconds": summary.get('duration'),
                "moving_duration_seconds": summary.get('movingDuration'),
                "elapsed_duration_seconds": summary.get('elapsedDuration'),
                "calories": summary.get('calories'),
                "avg_hr_bpm": summary.get('averageHR'),
                "max_hr_bpm": summary.get('maxHR'),
                "avg_speed_mps": summary.get('averageSpeed'),
                "max_speed_mps": summary.get('maxSpeed'),
                "avg_pace_min_per_km": summary.get('averagePace'),
                "elevation_gain_meters": summary.get('elevationGain'),
                "elevation_loss_meters": summary.get('elevationLoss'),
                "max_elevation_meters": summary.get('maxElevation'),
                "min_elevation_meters": summary.get('minElevation'),
                "avg_cadence": summary.get('averageRunCadence') or summary.get('averageBikeCadence'),
                "avg_power_watts": summary.get('averagePower'),
                "max_power_watts": summary.get('maxPower'),
                "normalized_power_watts": summary.get('normPower'),
                "training_effect_aerobic": summary.get('trainingEffectAerobic'),
                "training_effect_anaerobic": summary.get('trainingEffectAnaerobic'),
                "steps": summary.get('steps'),
                "strokes": summary.get('strokes'),
            }
            curated = {k: v for k, v in curated.items() if v is not None}
            return json.dumps(curated, indent=2)
        except Exception as e:
            return f"Error retrieving activity details: {str(e)}"

    @app.tool()
    async def get_activity_splits(activity_id: int) -> str:
        """Get lap/split data for an activity.

        Args:
            activity_id: The activity ID
        """
        try:
            splits = garmin_client.get_activity_splits(activity_id)
            if not splits:
                return f"No splits found for activity {activity_id}"
            return json.dumps(splits, indent=2)
        except Exception as e:
            return f"Error retrieving activity splits: {str(e)}"

    @app.tool()
    async def get_activity_hr_in_timezones(activity_id: int) -> str:
        """Get heart rate time in zones for an activity.

        Args:
            activity_id: The activity ID
        """
        try:
            hr_zones = garmin_client.get_activity_hr_in_timezones(activity_id)
            if not hr_zones:
                return f"No HR zone data found for activity {activity_id}"
            return json.dumps(hr_zones, indent=2)
        except Exception as e:
            return f"Error retrieving HR zones: {str(e)}"

    @app.tool()
    async def get_activity_weather(activity_id: int) -> str:
        """Get weather conditions during an activity.

        Args:
            activity_id: The activity ID
        """
        try:
            weather = garmin_client.get_activity_weather(activity_id)
            if not weather:
                return f"No weather data found for activity {activity_id}"
            return json.dumps(weather, indent=2)
        except Exception as e:
            return f"Error retrieving weather data: {str(e)}"

    @app.tool()
    async def set_activity_name(activity_id: int, name: str) -> str:
        """Rename an activity.

        Args:
            activity_id: The activity ID to rename
            name: The new name for the activity
        """
        try:
            garmin_client.set_activity_name(activity_id, name)
            return json.dumps({
                "status": "success",
                "activity_id": activity_id,
                "new_name": name,
            }, indent=2)
        except Exception as e:
            return f"Error renaming activity: {str(e)}"

    @app.tool()
    async def set_activity_type(activity_id: int, activity_type: str) -> str:
        """Change the type of an activity.

        Args:
            activity_id: The activity ID
            activity_type: The new activity type key (e.g., 'running', 'cycling', 'walking')
        """
        try:
            # Get current activity to preserve other fields
            url = f"{garmin_client.garmin_connect_activity}/{activity_id}"
            body = {
                "activityId": activity_id,
                "activityType": {"typeKey": activity_type},
            }
            garmin_client.client.put("connectapi", url, json=body, api=True)
            return json.dumps({
                "status": "success",
                "activity_id": activity_id,
                "new_type": activity_type,
            }, indent=2)
        except Exception as e:
            return f"Error changing activity type: {str(e)}"

    @app.tool()
    async def get_activity_types() -> str:
        """Get all available activity types from Garmin Connect."""
        try:
            types = garmin_client.get_activity_types()
            if not types:
                return "No activity types found"

            curated = []
            for t in types:
                curated.append({
                    "type_key": t.get('typeKey'),
                    "type_id": t.get('typeId'),
                    "parent_type": t.get('parentTypeId'),
                })
            return json.dumps(curated, indent=2)
        except Exception as e:
            return f"Error retrieving activity types: {str(e)}"
