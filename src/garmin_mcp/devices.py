"""
Device Management functions for Garmin Connect MCP Server
"""
import json

# The garmin_client will be set by the main file
garmin_client = None


def configure(client):
    """Configure the module with the Garmin client instance"""
    global garmin_client
    garmin_client = client


def register_tools(app):
    """Register all device management tools with the MCP server app"""

    @app.tool()
    async def get_devices() -> str:
        """Get all registered Garmin devices.

        Returns a list of all Garmin devices linked to the account,
        including model, firmware version, and battery status.
        """
        try:
            devices = garmin_client.get_devices()
            if not devices:
                return "No devices found"

            curated = []
            for d in devices:
                device = {
                    "device_id": d.get('deviceId'),
                    "display_name": d.get('displayName'),
                    "product_display_name": d.get('productDisplayName'),
                    "firmware_version": d.get('currentFirmwareVersion'),
                    "unit_id": d.get('unitId'),
                    "battery_status": d.get('batteryStatus'),
                    "battery_level": d.get('batteryLevel'),
                }
                device = {k: v for k, v in device.items() if v is not None}
                curated.append(device)

            return json.dumps(curated, indent=2)
        except Exception as e:
            return f"Error retrieving devices: {str(e)}"

    @app.tool()
    async def get_device_settings(device_id: int) -> str:
        """Get settings for a specific device.

        Args:
            device_id: The device ID (from get_devices)
        """
        try:
            settings = garmin_client.get_device_settings(device_id)
            if not settings:
                return f"No settings found for device {device_id}"
            return json.dumps(settings, indent=2)
        except Exception as e:
            return f"Error retrieving device settings: {str(e)}"

    @app.tool()
    async def get_device_last_used() -> str:
        """Get information about the last used Garmin device."""
        try:
            device = garmin_client.get_device_last_used()
            if not device:
                return "No last used device found"
            return json.dumps(device, indent=2)
        except Exception as e:
            return f"Error retrieving last used device: {str(e)}"

    @app.tool()
    async def get_primary_training_device() -> str:
        """Get the primary training device."""
        try:
            device = garmin_client.get_primary_training_device()
            if not device:
                return "No primary training device found"
            return json.dumps(device, indent=2)
        except Exception as e:
            return f"Error retrieving primary training device: {str(e)}"

    @app.tool()
    async def get_device_solar_data(date: str) -> str:
        """Get solar charging data for solar-equipped devices.

        Args:
            date: Date in YYYY-MM-DD format
        """
        try:
            solar = garmin_client.get_device_solar_data(date)
            if not solar:
                return f"No solar data found for {date}"
            return json.dumps(solar, indent=2)
        except Exception as e:
            return f"Error retrieving solar data: {str(e)}"
