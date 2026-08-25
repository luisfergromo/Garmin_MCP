"""Token management utilities for Garmin MCP authentication."""

import os
from pathlib import Path

from garminconnect import Garmin, GarminConnectConnectionError


def resolve_token_path(path: str) -> str:
    """Resolve environment variables and the user-home marker in a token path.

    Some MCP clients leave ``${HOME}`` unresolved when it comes from a nested
    user-config default. The explicit replacement also covers Windows, where
    ``HOME`` may be unset but Python can still resolve ``~`` via ``USERPROFILE``.
    """
    expanded = os.path.expandvars(path)
    expanded = expanded.replace("${HOME}", os.path.expanduser("~"))
    return os.path.expanduser(expanded)


def secure_token_dir(path: str) -> None:
    """Set owner-only permissions on a token directory and the files inside it.

    OAuth tokens are ~6-month bearer credentials to the full Garmin account, so
    they must not be left world-readable on multi-user hosts. Safe to call on a
    path that is a single file rather than a directory.
    """
    expanded = resolve_token_path(path)
    if not os.path.exists(expanded):
        return
    try:
        if os.path.isdir(expanded):
            os.chmod(expanded, 0o700)
            for entry in os.scandir(expanded):
                if entry.is_file():
                    os.chmod(entry.path, 0o600)
        else:
            os.chmod(expanded, 0o600)
    except OSError:
        # Windows may not support chmod the same way; skip silently
        pass


def get_token_path() -> str:
    """Get token path from environment or default.

    Returns:
        str: Path to token storage directory
    """
    return resolve_token_path(os.getenv("GARMINTOKENS") or "~/.garminconnect")


def get_token_base64_path() -> str:
    """Get base64 token file path from environment or default.

    Returns:
        str: Path to base64 token file
    """
    return resolve_token_path(
        os.getenv("GARMINTOKENS_BASE64") or "~/.garminconnect_base64"
    )


def token_exists(token_path: str = None) -> bool:
    """Check if authentication tokens exist at the given path.

    Args:
        token_path: Path to token directory. Uses default if None.

    Returns:
        bool: True if tokens exist
    """
    path = token_path or get_token_path()
    expanded = resolve_token_path(path)
    return os.path.exists(expanded)


def validate_tokens(token_path: str = None, is_cn: bool = False) -> tuple[bool, str]:
    """Validate that saved tokens can authenticate with Garmin Connect.

    Args:
        token_path: Path to token directory. Uses default if None.
        is_cn: Whether to use Garmin Connect China.

    Returns:
        Tuple of (success: bool, message: str)
    """
    path = token_path or get_token_path()
    expanded = resolve_token_path(path)

    if not os.path.exists(expanded):
        return False, f"Token path does not exist: {expanded}"

    try:
        garmin = Garmin(is_cn=is_cn)
        garmin.login(expanded)
        name = garmin.get_full_name()
        if name:
            return True, f"Authenticated as: {name}"
        return False, "Session is not authenticated (no profile returned)"
    except GarminConnectConnectionError:
        return False, "Cannot connect to Garmin Connect. Check your network."
    except Exception as e:
        return False, f"Token validation failed: {str(e)}"


def get_token_info(token_path: str = None) -> dict:
    """Get information about saved tokens.

    Args:
        token_path: Path to token directory. Uses default if None.

    Returns:
        dict with token status information
    """
    path = token_path or get_token_path()
    expanded = resolve_token_path(path)

    info = {
        "path": expanded,
        "exists": os.path.exists(expanded),
    }

    if info["exists"]:
        if os.path.isdir(expanded):
            files = list(os.scandir(expanded))
            info["type"] = "directory"
            info["file_count"] = len(files)
        else:
            info["type"] = "file"
            info["size_bytes"] = os.path.getsize(expanded)

    return info
