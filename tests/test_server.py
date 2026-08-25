"""Basic tests for Garmin MCP server structure."""

import importlib


def test_module_imports():
    """Verify all tool modules can be imported."""
    tool_modules = [
        "garmin_mcp.activity_management",
        "garmin_mcp.health_wellness",
        "garmin_mcp.training",
        "garmin_mcp.devices",
        "garmin_mcp.gear_management",
        "garmin_mcp.weight_management",
        "garmin_mcp.workouts",
        "garmin_mcp.user_profile",
    ]
    for mod_name in tool_modules:
        mod = importlib.import_module(mod_name)
        assert hasattr(mod, "configure"), f"{mod_name} missing configure()"
        assert hasattr(mod, "register_tools"), f"{mod_name} missing register_tools()"

    # token_utils is a utility module, not a tool module
    token_mod = importlib.import_module("garmin_mcp.token_utils")
    assert hasattr(token_mod, "get_token_path")


def test_token_utils_functions():
    """Verify token_utils has expected functions."""
    from garmin_mcp import token_utils

    assert callable(token_utils.resolve_token_path)
    assert callable(token_utils.get_token_path)
    assert callable(token_utils.get_token_base64_path)
    assert callable(token_utils.token_exists)
    assert callable(token_utils.secure_token_dir)


def test_token_path_defaults():
    """Verify default token paths contain .garminconnect."""
    from garmin_mcp import token_utils

    path = token_utils.get_token_path()
    assert ".garminconnect" in path

    b64_path = token_utils.get_token_base64_path()
    assert ".garminconnect_base64" in b64_path


def test_resolve_token_path_tilde():
    """Verify tilde expansion works."""
    import os
    from garmin_mcp import token_utils

    result = token_utils.resolve_token_path("~/test")
    assert "~" not in result
    assert os.path.expanduser("~") in result
