"""
Workout Management functions for Garmin Connect MCP Server
"""
import json

# The garmin_client will be set by the main file
garmin_client = None


def configure(client):
    """Configure the module with the Garmin client instance"""
    global garmin_client
    garmin_client = client


def register_tools(app):
    """Register all workout management tools with the MCP server app"""

    @app.tool()
    async def get_workouts(limit: int = 20, start: int = 0) -> str:
        """Get saved workouts with pagination.

        Args:
            limit: Number of workouts to retrieve (default 20, max 100)
            start: Offset for pagination (default 0)
        """
        try:
            limit = min(max(1, limit), 100)
            workouts = garmin_client.get_workouts(start, limit)
            if not workouts:
                return "No workouts found"

            curated = {
                "count": len(workouts),
                "start": start,
                "limit": limit,
                "workouts": [],
            }

            for w in workouts:
                workout = {
                    "workout_id": w.get('workoutId'),
                    "name": w.get('workoutName'),
                    "sport_type": w.get('sportType', {}).get('sportTypeKey'),
                    "description": w.get('description'),
                    "estimated_duration_seconds": w.get('estimatedDurationInSecs'),
                    "created_date": w.get('createdDate'),
                    "updated_date": w.get('updatedDate'),
                }
                workout = {k: v for k, v in workout.items() if v is not None}
                curated["workouts"].append(workout)

            return json.dumps(curated, indent=2)
        except Exception as e:
            return f"Error retrieving workouts: {str(e)}"

    @app.tool()
    async def get_workout(workout_id: int) -> str:
        """Get detailed information about a specific workout.

        Args:
            workout_id: The workout ID
        """
        try:
            workout = garmin_client.get_workout(workout_id)
            if not workout:
                return f"No workout found with ID {workout_id}"
            return json.dumps(workout, indent=2)
        except Exception as e:
            return f"Error retrieving workout: {str(e)}"

    @app.tool()
    async def schedule_workout(workout_id: int, date: str) -> str:
        """Schedule a workout for a specific date.

        The workout will appear on your Garmin device's calendar after syncing.

        Args:
            workout_id: The workout ID to schedule
            date: Date in YYYY-MM-DD format
        """
        try:
            result = garmin_client.schedule_workout(workout_id, date)
            return json.dumps({
                "status": "success",
                "workout_id": workout_id,
                "scheduled_date": date,
                "response": result if result else "Workout scheduled",
            }, indent=2)
        except Exception as e:
            return f"Error scheduling workout: {str(e)}"

    @app.tool()
    async def delete_workout(workout_id: int) -> str:
        """Delete a saved workout.

        Args:
            workout_id: The workout ID to delete
        """
        try:
            result = garmin_client.delete_workout(workout_id)
            return json.dumps({
                "status": "success",
                "workout_id": workout_id,
                "response": result if result else "Workout deleted",
            }, indent=2)
        except Exception as e:
            return f"Error deleting workout: {str(e)}"

    @app.tool()
    async def get_workout_by_date(date: str) -> str:
        """Get workouts scheduled for a specific date.

        Args:
            date: Date in YYYY-MM-DD format
        """
        try:
            workouts = garmin_client.get_workout_by_date(date)
            if not workouts:
                return f"No workouts scheduled for {date}"
            return json.dumps(workouts, indent=2)
        except Exception as e:
            return f"Error retrieving scheduled workouts: {str(e)}"
