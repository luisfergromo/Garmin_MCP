"""
User Profile functions for Garmin Connect MCP Server
"""
import json

# The garmin_client will be set by the main file
garmin_client = None


def configure(client):
    """Configure the module with the Garmin client instance"""
    global garmin_client
    garmin_client = client


def register_tools(app):
    """Register all user profile tools with the MCP server app"""

    @app.tool()
    async def get_user_profile() -> str:
        """Get the user's Garmin Connect profile information.

        Returns profile details including display name, profile number,
        and user settings.
        """
        try:
            profile = garmin_client.get_user_profile()
            if not profile:
                return "No profile data found"

            curated = {
                "display_name": profile.get('displayName'),
                "profile_number": profile.get('profileNumber'),
                "user_name": profile.get('userName'),
                "profile_image_url": profile.get('profileImageUrl'),
            }
            curated = {k: v for k, v in curated.items() if v is not None}
            return json.dumps(curated, indent=2)
        except Exception as e:
            return f"Error retrieving user profile: {str(e)}"

    @app.tool()
    async def get_full_name() -> str:
        """Get the user's full name from Garmin Connect."""
        try:
            name = garmin_client.get_full_name()
            if not name:
                return "Could not retrieve full name"
            return json.dumps({"full_name": name}, indent=2)
        except Exception as e:
            return f"Error retrieving full name: {str(e)}"

    @app.tool()
    async def get_unit_system() -> str:
        """Get the user's preferred unit system (metric/imperial)."""
        try:
            units = garmin_client.get_unit_system()
            if not units:
                return "Could not retrieve unit system"
            return json.dumps(units, indent=2)
        except Exception as e:
            return f"Error retrieving unit system: {str(e)}"
