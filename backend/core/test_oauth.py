"""Test OAuth credentials and mock mode for development.

This module provides:
1. Mock OAuth flow for testing without real credentials
2. Test credential loading from environment
3. OAuth URL generation for testing
"""
import os
from typing import Dict, Optional

# Test OAuth Apps Configuration
TEST_OAUTH_APPS = {
    "pinterest": {
        "client_id": os.getenv("TEST_PINTEREST_CLIENT_ID", "test-pinterest-client-id"),
        "client_secret": os.getenv("TEST_PINTEREST_CLIENT_SECRET", "test-pinterest-secret"),
        "redirect_uri": os.getenv("TEST_PINTEREST_REDIRECT_URI", "http://localhost:8000/api/auth/pinterest/callback"),
        "authorization_url": "https://www.pinterest.com/oauth/",
        "token_url": "https://api.pinterest.com/v5/oauth/token",
    },
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
    }
}

def get_test_oauth_config(platform: str) -> Dict:
    """Get OAuth configuration for testing.
    
    Args:
        platform: 'pinterest', 'linkedin', or 'x'
        
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
    
    if platform == "pinterest":
        params = {
            "client_id": config.get("client_id"),
            "redirect_uri": config.get("redirect_uri"),
            "response_type": "code",
            "scope": "boards:read,boards:write,pins:read,pins:write",
            "state": state,
        }
        query = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{config.get('authorization_url')}?{query}"
    
    elif platform == "linkedin":
        params = {
            "client_id": config.get("client_id"),
            "redirect_uri": config.get("redirect_uri"),
            "response_type": "code",
            "scope": "openid,profile,email,w_member_social",
            "state": state,
        }
        query = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{config.get('authorization_url')}?{query}"
    
    return ""

def simulate_oauth_callback(platform: str, code: str) -> Dict:
    """Simulate OAuth callback for testing.
    
    Returns mock token data that looks like real OAuth response.
    """
    if platform == "pinterest":
        return {
            "access_token": f"test-pinterest-token-{code[:8]}",
            "refresh_token": f"test-pinterest-refresh-{code[:8]}",
            "token_type": "Bearer",
            "expires_in": 3600,
            "account_id": "test-account-123",
            "account_name": "@testuser",
            "profile_image": "https://i.pinimg.com/test.jpg",
        }
    
    elif platform == "linkedin":
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
    
    return {}

def validate_test_credentials(platform: str) -> bool:
    """Validate that test credentials are configured.
    
    Returns True if credentials are set (not defaults).
    """
    config = get_test_oauth_config(platform)
    
    if platform in ["pinterest", "linkedin"]:
        client_id = config.get("client_id", "")
        return not client_id.startswith("test-") and len(client_id) > 10
    
    elif platform == "x":
        api_key = config.get("api_key", "")
        return not api_key.startswith("test-") and len(api_key) > 10
    
    return False

# Quick test
if __name__ == "__main__":
    print("Test OAuth Configuration:")
    print(f"Mock Mode: {is_test_mode()}")
    print(f"Pinterest Config: {get_test_oauth_config('pinterest')}")
    print(f"LinkedIn Config: {get_test_oauth_config('linkedin')}")
    
    # Test URL generation
    url = generate_test_authorization_url("pinterest", "test-state-123")
    print(f"\nTest Pinterest URL:\n{url}")
