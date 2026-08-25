"""
Weight Management functions for Garmin Connect MCP Server
"""
import json

# The garmin_client will be set by the main file
garmin_client = None


def configure(client):
    """Configure the module with the Garmin client instance"""
    global garmin_client
    garmin_client = client


def register_tools(app):
    """Register all weight management tools with the MCP server app"""

    @app.tool()
    async def get_weigh_ins(start_date: str, end_date: str) -> str:
        """Get weight measurements for a date range.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
        """
        try:
            weigh_ins = garmin_client.get_weigh_ins(start_date, end_date)
            if not weigh_ins:
                return f"No weigh-ins found between {start_date} and {end_date}"
            return json.dumps(weigh_ins, indent=2)
        except Exception as e:
            return f"Error retrieving weigh-ins: {str(e)}"

    @app.tool()
    async def get_daily_weigh_ins(date: str) -> str:
        """Get weight measurements for a specific date.

        Args:
            date: Date in YYYY-MM-DD format
        """
        try:
            weigh_ins = garmin_client.get_daily_weigh_ins(date)
            if not weigh_ins:
                return f"No weigh-ins found for {date}"
            return json.dumps(weigh_ins, indent=2)
        except Exception as e:
            return f"Error retrieving daily weigh-ins: {str(e)}"

    @app.tool()
    async def get_weigh_ins_latest() -> str:
        """Get the most recent weight measurement."""
        try:
            latest = garmin_client.get_weigh_ins_daily_latest()
            if not latest:
                return "No recent weigh-in data found"
            return json.dumps(latest, indent=2)
        except Exception as e:
            return f"Error retrieving latest weigh-in: {str(e)}"

    @app.tool()
    async def add_weigh_in(weight_kg: float, date: str = None) -> str:
        """Record a new weight measurement.

        Args:
            weight_kg: Weight in kilograms
            date: Optional date in YYYY-MM-DD format (defaults to today)
        """
        try:
            if date:
                result = garmin_client.add_weigh_in(weight=weight_kg, unitKey="kg", date=date)
            else:
                result = garmin_client.add_weigh_in(weight=weight_kg, unitKey="kg")

            return json.dumps({
                "status": "success",
                "weight_kg": weight_kg,
                "date": date or "today",
                "response": result if result else "Weight recorded",
            }, indent=2)
        except Exception as e:
            return f"Error adding weigh-in: {str(e)}"
