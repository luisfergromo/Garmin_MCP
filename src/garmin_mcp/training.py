"""
Training & Performance functions for Garmin Connect MCP Server
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
    """Register all training and performance tools with the MCP server app"""

    @app.tool()
    async def get_training_status(date: str) -> str:
        """Get training status for a specific date.

        Shows current training load, status (productive, maintaining, etc.),
        and recent training history.

        Args:
            date: Date in YYYY-MM-DD format
        """
        try:
            status = garmin_client.get_training_status(date)
            if not status:
                return f"No training status found for {date}"
            return json.dumps(status, indent=2)
        except Exception as e:
            return f"Error retrieving training status: {str(e)}"

    @app.tool()
    async def get_training_readiness(date: str) -> str:
        """Get training readiness score for a specific date.

        Training Readiness evaluates your recovery, training load, sleep,
        and stress to indicate how ready you are for training.

        Args:
            date: Date in YYYY-MM-DD format
        """
        try:
            readiness = garmin_client.get_training_readiness(date)
            if not readiness:
                return f"No training readiness data found for {date}"
            return json.dumps(readiness, indent=2)
        except Exception as e:
            return f"Error retrieving training readiness: {str(e)}"

    @app.tool()
    async def get_max_metrics(date: str) -> str:
        """Get VO2 max and other maximum metrics for a date.

        Returns estimated VO2 max values for running and cycling,
        along with fitness age and other peak performance indicators.

        Args:
            date: Date in YYYY-MM-DD format
        """
        try:
            metrics = garmin_client.get_max_metrics(date)
            if not metrics:
                return f"No max metrics found for {date}"
            return json.dumps(metrics, indent=2)
        except Exception as e:
            return f"Error retrieving max metrics: {str(e)}"

    @app.tool()
    async def get_hill_score(date: str) -> str:
        """Get hill score data for a specific date.

        Hill Score measures your ability to run uphill based on
        recent training history and fitness level.

        Args:
            date: Date in YYYY-MM-DD format
        """
        try:
            score = garmin_client.get_hill_score(date)
            if not score:
                return f"No hill score data found for {date}"
            return json.dumps(score, indent=2)
        except Exception as e:
            return f"Error retrieving hill score: {str(e)}"

    @app.tool()
    async def get_endurance_score(date: str) -> str:
        """Get endurance score data for a specific date.

        Endurance Score reflects your overall aerobic endurance capacity
        based on training history and physiological metrics.

        Args:
            date: Date in YYYY-MM-DD format
        """
        try:
            score = garmin_client.get_endurance_score(date)
            if not score:
                return f"No endurance score data found for {date}"
            return json.dumps(score, indent=2)
        except Exception as e:
            return f"Error retrieving endurance score: {str(e)}"

    @app.tool()
    async def get_race_predictions() -> str:
        """Get race time predictions based on current fitness level.

        Returns estimated race times for 5K, 10K, half marathon, and marathon
        distances based on your VO2 max and training data.
        """
        try:
            predictions = garmin_client.get_race_predictions()
            if not predictions:
                return "No race predictions available"
            return json.dumps(predictions, indent=2)
        except Exception as e:
            return f"Error retrieving race predictions: {str(e)}"

    @app.tool()
    async def get_personal_record(owner_display_name: str) -> str:
        """Get personal records for a user.

        Args:
            owner_display_name: The Garmin display name of the user
        """
        try:
            records = garmin_client.get_personal_record(owner_display_name)
            if not records:
                return f"No personal records found for {owner_display_name}"
            return json.dumps(records, indent=2)
        except Exception as e:
            return f"Error retrieving personal records: {str(e)}"

    @app.tool()
    async def get_earned_badges() -> str:
        """Get all earned badges/achievements from Garmin Connect."""
        try:
            badges = garmin_client.get_earned_badges()
            if not badges:
                return "No earned badges found"
            return json.dumps(badges, indent=2)
        except Exception as e:
            return f"Error retrieving earned badges: {str(e)}"
