"""Test OAuth credentials and mock mode for development.

This module provides:
1. Mock OAuth flow for testing without real credentials
2. Test credential loading from environment
3. OAuth URL generation for testing

Updated 2026-03-23: Pinterest removed, added Instagram, Facebook, TikTok stubs
"""
import os
from typing import Dict, Optional

# Test OAuth Apps Configuration
# Pinterest REMOVED 2026-03-23 (rejected business application)
TEST_OAUTH_APPS = {
    "linkedin": {
        "client_id": os.getenv("TEST_LINKEDIN_CLIENT_ID", "test-linkedin-client-id"),
        "client_secret": os.getenv("TEST_LINKEDIN_CLIENT_SECRET", "test-linkedin-secret"),
        "redirect_uri": os.getenv("TEST_LINKEDIN_REDIRECT_URI", "http://localhost:8000/api/auth/linkedin/callback"),
        "authorization_url": "https://www.linkedin.com/oauth/v2/authorization",
        "token_url": "https://www.linkedin.com/oauth/v2/accessToken",
    },
    "x": {
        "api_key": os.getenv("TEST_X_API_KEY", "test-x-api-key"),
        "api_secret": os.getenv("TEST_X_API_SECRET", "test-x-api-secret"),
        "redirect_uri": os.getenv("TEST_X_REDIRECT_URI", "http://localhost:8000/api/auth/x/callback"),
        "request_token_url": "https://api.twitter.com/oauth/request_token",
        "authorization_url": "https://api.twitter.com/oauth/authorize",
        "access_token_url": "https://api.twitter.com/oauth/access_token",
    },
    # Instagram uses Meta OAuth (same as Facebook)
    "instagram": {
        "client_id": os.getenv("TEST_INSTAGRAM_CLIENT_ID", "test-instagram-client-id"),
        "client_secret": os.getenv("TEST_INSTAGRAM_CLIENT_SECRET", "test-instagram-secret"),
        "redirect_uri": os.getenv("TEST_INSTAGRAM_REDIRECT_URI", "http://localhost:8000/api/auth/instagram/callback"),
        "authorization_url": "https://api.instagram.com/oauth/authorize",
        "token_url": "https://api.instagram.com/oauth/access_token",
    },
    # Facebook uses Meta OAuth
    "facebook": {
        "client_id": os.getenv("TEST_FACEBOOK_CLIENT_ID", "test-facebook-client-id"),
        "client_secret": os.getenv("TEST_FACEBOOK_CLIENT_SECRET", "test-facebook-secret"),
        "redirect_uri": os.getenv("TEST_FACEBOOK_REDIRECT_URI", "http://localhost:8000/api/auth/facebook/callback"),
        "authorization_url": "https://www.facebook.com/v18.0/dialog/oauth",
        "token_url": "https://graph.facebook.com/v18.0/oauth/access_token",
    },
    # TikTok OAuth
    "tiktok": {
        "client_key": os.getenv("TEST_TIKTOK_CLIENT_KEY", "test-tiktok-client-key"),
        "client_secret": os.getenv("TEST_TIKTOK_CLIENT_SECRET", "test-tiktok-secret"),
        "redirect_uri": os.getenv("TEST_TIKTOK_REDIRECT_URI", "http://localhost:8000/api/auth/tiktok/callback"),
        "authorization_url": "https://www.tiktok.com/v2/auth/authorize",
        "token_url": "https://open.tiktokapis.com/v2/oauth/token",
    },
}


def get_test_oauth_config(platform: str) -> Dict:
    """Get OAuth configuration for testing.

    Args:
        platform: 'linkedin', 'x', 'instagram', 'facebook', or 'tiktok'

    Returns:
        Dict with OAuth endpoints and credentials
    """
    return TEST_OAUTH_APPS.get(platform, {})


def is_test_mode() -> bool:
    """Check if running in test/mock mode."""
    return os.getenv("MOCK_OAUTH", "false").lower() == "true"


def generate_test_authorization_url(platform: str, state: str) -> str:
    """Generate OAuth authorization URL for testing.

    In test mode, this returns a simulated URL.
    In production, this returns the real platform URL.
    """
    config = get_test_oauth_config(platform)

    if platform == "linkedin":
        params = {
            "client_id": config.get("client_id"),
            "redirect_uri": config.get("redirect_uri"),
            "response_type": "code",
            "scope": "openid,profile,email,w_member_social",
            "state": state,
        }
        query = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{config.get('authorization_url')}?{query}"

    elif platform == "x":
        params = {
            "oauth_consumer_key": config.get("api_key"),
            "oauth_callback": config.get("redirect_uri"),
            "oauth_token": config.get("request_token"),
            "state": state,
        }
        # OAuth 1.0a — return a mock URL
        return f"{config.get('authorization_url')}?oauth_token={config.get('request_token', 'test-token')}&state={state}"

    elif platform == "instagram":
        params = {
            "client_id": config.get("client_id"),
            "redirect_uri": config.get("redirect_uri"),
            "scope": "user_profile,user_media",
            "response_type": "code",
            "state": state,
        }
        query = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{config.get('authorization_url')}?{query}"

    elif platform == "facebook":
        params = {
            "client_id": config.get("client_id"),
            "redirect_uri": config.get("redirect_uri"),
            "scope": "pages_manage_posts,pages_read_engagement,instagram_basic,instagram_content_publish",
            "response_type": "code",
            "state": state,
        }
        query = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{config.get('authorization_url')}?{query}"

    elif platform == "tiktok":
        params = {
            "client_key": config.get("client_key"),
            "redirect_uri": config.get("redirect_uri"),
            "scope": "user.info.basic,video.upload,video.publish",
            "response_type": "code",
            "state": state,
        }
        query = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{config.get('authorization_url')}?{query}"

    return ""


def simulate_oauth_callback(platform: str, code: str) -> Dict:
    """Simulate OAuth callback for testing.

    Returns mock token data that looks like real OAuth response.
    """
    if platform == "linkedin":
        return {
            "access_token": f"test-linkedin-token-{code[:8]}",
            "refresh_token": f"test-linkedin-refresh-{code[:8]}",
            "token_type": "Bearer",
            "expires_in": 5184000,
            "account_id": "urn:li:person:test123",
            "account_name": "Test User",
            "profile_image": "https://media.licdn.com/test.jpg",
        }

    elif platform == "x":
        return {
            "access_token": f"test-x-token-{code[:8]}",
            "token_secret": f"test-x-secret-{code[:8]}",
            "token_type": "OAuth1.0a",
            "account_id": "123456789",
            "account_name": "@testuser",
            "profile_image": "https://pbs.twimg.com/test.jpg",
        }

    elif platform == "instagram":
        return {
            "access_token": f"test-instagram-token-{code[:8]}",
            "token_type": "Bearer",
            "expires_in": 5184000,
            "account_id": "17841400000000000",
            "account_name": "@testuser",
            "profile_image": "https://scontent.cdninstagram.com/test.jpg",
        }

    elif platform == "facebook":
        return {
            "access_token": f"test-facebook-token-{code[:8]}",
            "token_type": "Bearer",
            "expires_in": 5184000,
            "account_id": "1234567890123456",
            "account_name": "Test Page",
            "profile_image": "https://scontent.xx.fbcdn.net/test.jpg",
        }

    elif platform == "tiktok":
        return {
            "access_token": f"test-tiktok-token-{code[:8]}",
            "refresh_token": f"test-tiktok-refresh-{code[:8]}",
            "open_id": f"test-openid-{code[:8]}",
            "expires_in": 86400,
            "account_id": "1234567890123456789",
            "account_name": "@testuser",
            "profile_image": "https://p16-p.tiktokcdn.com/test.jpg",
        }

    return {}


def validate_test_credentials(platform: str) -> bool:
    """Validate that test credentials are configured.

    Returns True if credentials are set (not defaults).
    """
    config = get_test_oauth_config(platform)

    if platform in ["linkedin", "instagram", "facebook"]:
        client_id = config.get("client_id", "")
        return not client_id.startswith("test-") and len(client_id) > 10

    elif platform == "x":
        api_key = config.get("api_key", "")
        return not api_key.startswith("test-") and len(api_key) > 10

    elif platform == "tiktok":
        client_key = config.get("client_key", "")
        return not client_key.startswith("test-") and len(client_key) > 10

    return False


# Quick test
if __name__ == "__main__":
    print("Test OAuth Configuration:")
    print(f"Mock Mode: {is_test_mode()}")
    print(f"LinkedIn Config: {get_test_oauth_config('linkedin')}")
    print(f"Instagram Config: {get_test_oauth_config('instagram')}")
    print(f"Facebook Config: {get_test_oauth_config('facebook')}")
    print(f"TikTok Config: {get_test_oauth_config('tiktok')}")

    # Test URL generation
    url = generate_test_authorization_url("instagram", "test-state-123")
    print(f"\nTest Instagram URL:\n{url}")
