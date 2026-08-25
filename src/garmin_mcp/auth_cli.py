"""Pre-authentication CLI tool for Garmin MCP server.

This tool allows users to authenticate with Garmin Connect and save OAuth tokens
before running the MCP server in non-interactive environments like Gemini or Claude Desktop.
"""

import argparse
import os
import sys
import getpass
import base64

import requests
from garminconnect import (
    Garmin,
    GarminConnectAuthenticationError,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
)

from garmin_mcp.token_utils import (
    get_token_path,
    get_token_base64_path,
    token_exists,
    validate_tokens,
    get_token_info,
    resolve_token_path,
    secure_token_dir,
)


def get_mfa() -> str:
    """Get MFA code from user input."""
    print("\nGarmin Connect MFA required. Please check your email/phone for the code.")
    return input("Enter MFA code: ")


def get_credentials() -> tuple[str, str]:
    """Get credentials from environment variables or user input.

    Returns:
        Tuple of (email, password)

    Raises:
        ValueError: If credentials cannot be obtained
    """
    # Try environment variables first
    email = os.environ.get("GARMIN_EMAIL")
    email_file = os.environ.get("GARMIN_EMAIL_FILE")

    if email and email_file:
        raise ValueError(
            "Must only provide one of GARMIN_EMAIL and GARMIN_EMAIL_FILE, got both"
        )
    elif email_file:
        with open(email_file, "r") as f:
            email = f.read().rstrip()

    password = os.environ.get("GARMIN_PASSWORD")
    password_file = os.environ.get("GARMIN_PASSWORD_FILE")

    if password and password_file:
        raise ValueError(
            "Must only provide one of GARMIN_PASSWORD and GARMIN_PASSWORD_FILE, got both"
        )
    elif password_file:
        with open(password_file, "r") as f:
            password = f.read().rstrip()

    # Prompt for missing credentials
    if not email:
        print("\nGarmin Connect Credentials")
        print("-" * 40)
        email = input("Email: ").strip()
        if not email:
            raise ValueError("Email is required")

    if not password:
        password = getpass.getpass("Password: ")
        if not password:
            raise ValueError("Password is required")

    return email, password


def authenticate(
    token_path: str,
    token_base64_path: str,
    force_reauth: bool = False,
    is_cn: bool = False,
) -> bool:
    """Authenticate with Garmin Connect and save tokens.

    Args:
        token_path: Path to save token directory
        token_base64_path: Path to save base64 token file
        force_reauth: Force re-authentication even if tokens exist
        is_cn: Use Garmin Connect China (garmin.cn) instead of international

    Returns:
        bool: True if authentication was successful
    """
    expanded_path = resolve_token_path(token_path)

    if not force_reauth and token_exists(token_path):
        print(f"\nTokens already exist at: {expanded_path}")
        valid, msg = validate_tokens(token_path, is_cn=is_cn)
        if valid:
            print(f"[OK] {msg}")
            return True
        print(f"[FAIL] {msg}")
        print("Proceeding with re-authentication...")

    try:
        email, password = get_credentials()

        print(f"\nAuthenticating with Garmin Connect{'  (China)' if is_cn else ''}...")
        garmin = Garmin(email=email, password=password, is_cn=is_cn, prompt_mfa=get_mfa)
        garmin.login()

        # Save tokens
        garmin.client.dump(expanded_path)
        print(f"\n[OK] Tokens saved to: {expanded_path}")

        # Save base64 tokens
        expanded_base64 = resolve_token_path(token_base64_path)
        token_bytes = garmin.client.dumps()
        encoded = base64.b64encode(token_bytes.encode()).decode()
        with open(expanded_base64, "w") as f:
            f.write(encoded)
        print(f"[OK] Base64 tokens saved to: {expanded_base64}")

        # Secure permissions
        secure_token_dir(token_path)
        secure_token_dir(token_base64_path)

        # Verify
        name = garmin.get_full_name()
        if name:
            print(f"\n[OK] Successfully authenticated as: {name}")
        else:
            print("\n[WARN] Authenticated but could not retrieve profile name")

        return True

    except GarminConnectAuthenticationError as e:
        print(f"\n[FAIL] Authentication failed: {e}", file=sys.stderr)
        return False
    except GarminConnectTooManyRequestsError:
        print(
            "\n[FAIL] Too many login attempts. Wait a few minutes before retrying.",
            file=sys.stderr,
        )
        return False
    except GarminConnectConnectionError:
        print(
            "\n[FAIL] Cannot connect to Garmin Connect. Check your network.",
            file=sys.stderr,
        )
        return False
    except ValueError as e:
        print(f"\n✗ {e}", file=sys.stderr)
        return False
    except KeyboardInterrupt:
        print("\n\nCancelled.", file=sys.stderr)
        return False


def main():
    """CLI entry point for garmin-mcp-auth."""
    parser = argparse.ArgumentParser(
        description="Authenticate with Garmin Connect and save OAuth tokens for the MCP server."
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Only verify existing tokens without re-authenticating",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-authentication even if valid tokens exist",
    )
    parser.add_argument(
        "--is-cn",
        action="store_true",
        help="Use Garmin Connect China (garmin.cn) instead of international",
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Show token storage information",
    )

    args = parser.parse_args()

    is_cn = args.is_cn or os.getenv("GARMIN_IS_CN", "false").lower() in (
        "true",
        "1",
        "yes",
    )
    token_path = get_token_path()
    token_base64_path = get_token_base64_path()

    if args.info:
        info = get_token_info(token_path)
        print("\nToken Storage Info")
        print("-" * 40)
        for key, value in info.items():
            print(f"  {key}: {value}")
        sys.exit(0)

    if args.verify:
        if not token_exists(token_path):
            print(f"\n[FAIL] No tokens found at: {resolve_token_path(token_path)}")
            print("Run 'garmin-mcp-auth' to authenticate.")
            sys.exit(1)

        valid, msg = validate_tokens(token_path, is_cn=is_cn)
        if valid:
            print(f"\n[OK] {msg}")
            sys.exit(0)
        else:
            print(f"\n[FAIL] {msg}")
            sys.exit(1)

    success = authenticate(
        token_path, token_base64_path, force_reauth=args.force, is_cn=is_cn
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
