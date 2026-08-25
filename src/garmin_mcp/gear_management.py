"""
Gear Management functions for Garmin Connect MCP Server
"""
import json

# The garmin_client will be set by the main file
garmin_client = None


def configure(client):
    """Configure the module with the Garmin client instance"""
    global garmin_client
    garmin_client = client


def register_tools(app):
    """Register all gear management tools with the MCP server app"""

    @app.tool()
    async def get_gear(user_profile_number: int) -> str:
        """Get all gear/equipment for a user.

        Args:
            user_profile_number: The user's profile number (from get_user_profile)
        """
        try:
            gear = garmin_client.get_gear(user_profile_number)
            if not gear:
                return "No gear found"
            return json.dumps(gear, indent=2)
        except Exception as e:
            return f"Error retrieving gear: {str(e)}"

    @app.tool()
    async def get_gear_stats(gear_uuid: str) -> str:
        """Get statistics for a specific piece of gear.

        Args:
            gear_uuid: The UUID of the gear item
        """
        try:
            stats = garmin_client.get_gear_stats(gear_uuid)
            if not stats:
                return f"No stats found for gear {gear_uuid}"
            return json.dumps(stats, indent=2)
        except Exception as e:
            return f"Error retrieving gear stats: {str(e)}"

    @app.tool()
    async def get_gear_defaults(user_profile_number: int) -> str:
        """Get default gear assignments for activity types.

        Args:
            user_profile_number: The user's profile number
        """
        try:
            defaults = garmin_client.get_gear_defaults(user_profile_number)
            if not defaults:
                return "No gear defaults found"
            return json.dumps(defaults, indent=2)
        except Exception as e:
            return f"Error retrieving gear defaults: {str(e)}"

    @app.tool()
    async def get_activity_gear(activity_id: int) -> str:
        """Get gear used in a specific activity.

        Args:
            activity_id: The activity ID
        """
        try:
            gear = garmin_client.get_activity_gear(activity_id)
            if not gear:
                return f"No gear found for activity {activity_id}"
            return json.dumps(gear, indent=2)
        except Exception as e:
            return f"Error retrieving activity gear: {str(e)}"
