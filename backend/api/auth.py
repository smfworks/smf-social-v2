"""OAuth routes for social media platform connections.
Now with test/mock mode support for development."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional
import secrets

from core.database import get_db
from core.security import verify_token, encrypt_token
from core.test_oauth import (
    is_test_mode, 
    generate_test_authorization_url, 
    simulate_oauth_callback,
    get_test_oauth_config
)
from models.sqlite_database import OAuthApp, Integration, Tenant
from providers.pinterest import PinterestProvider
from providers.linkedin import LinkedInProvider

router = APIRouter(prefix="/auth", tags=["auth"])

# Store state temporarily (use Redis in production)
oauth_states = {}

def get_or_create_test_oauth_app(db: Session, tenant_id: str, platform: str):
    """Get existing OAuth app or create test one."""
    oauth_app = db.query(OAuthApp).filter(
        OAuthApp.tenant_id == tenant_id,
        OAuthApp.platform == platform
    ).first()
    
    if oauth_app:
        return oauth_app
    
    # Create test OAuth app
    test_config = get_test_oauth_config(platform)
    
    oauth_app = OAuthApp(
        tenant_id=tenant_id,
        platform=platform,
        client_id=test_config.get("client_id", f"test-{platform}"),
        client_secret=test_config.get("client_secret", f"test-secret-{platform}"),
        redirect_uri=test_config.get("redirect_uri", f"http://localhost:8000/api/auth/{platform}/callback"),
        app_name=f"Test {platform.title()} App",
        is_active=True
    )
    
    db.add(oauth_app)
    db.commit()
    db.refresh(oauth_app)
    
    return oauth_app

@router.get("/{platform}/connect")
def connect_platform(
    platform: str,
    tenant_id: str,
    test: Optional[bool] = False,
    db: Session = Depends(get_db)
):
    """Start OAuth flow for a platform.
    
    Set test=true to use mock OAuth without real credentials.
    """
    # Use mock mode if requested or globally set
    use_mock = test or is_test_mode()
    
    if use_mock:
        # Generate test authorization URL
        state = secrets.token_urlsafe(32)
        oauth_states[state] = {
            "tenant_id": tenant_id,
            "platform": platform,
            "mock": True
        }
        
        auth_url = generate_test_authorization_url(platform, state)
        
        # Ensure test OAuth app exists
        get_or_create_test_oauth_app(db, tenant_id, platform)
        
        return {
            "authorization_url": auth_url,
            "mock_mode": True,
            "note": "Using test OAuth. Set real credentials in environment for production."
        }
    
    # Real OAuth flow
    oauth_app = db.query(OAuthApp).filter(
        OAuthApp.tenant_id == tenant_id,
        OAuthApp.platform == platform,
        OAuthApp.is_active == True
    ).first()
    
    if not oauth_app:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No OAuth app configured for {platform}. Use ?test=true for testing."
        )
    
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    oauth_states[state] = {
        "tenant_id": tenant_id,
        "platform": platform,
        "mock": False
    }
    
    # Get authorization URL
    credentials = {
        "client_id": oauth_app.client_id,
        "client_secret": oauth_app.client_secret,
        "redirect_uri": oauth_app.redirect_uri
    }
    
    if platform == "pinterest":
        provider = PinterestProvider(credentials)
        auth_url = provider.get_authorization_url(state=state)
    elif platform == "linkedin":
        provider = LinkedInProvider(credentials)
        auth_url = provider.get_authorization_url(state=state)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Platform {platform} not supported"
        )
    
    return {"authorization_url": auth_url, "mock_mode": False}


@router.get("/{platform}/callback")
def oauth_callback(
    platform: str,
    code: str,
    state: str,
    db: Session = Depends(get_db)
):
    """Handle OAuth callback from platform.
    
    Supports both real and mock OAuth callbacks.
    """
    # Verify state
    if state not in oauth_states:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid state parameter"
        )
    
    state_data = oauth_states.pop(state)
    tenant_id = state_data["tenant_id"]
    is_mock = state_data.get("mock", False)
    
    # Get or create OAuth app
    oauth_app = get_or_create_test_oauth_app(db, tenant_id, platform)
    
    try:
        if is_mock:
            # Mock OAuth - simulate token exchange
            token_data = simulate_oauth_callback(platform, code)
        else:
            # Real OAuth flow
            credentials = {
                "client_id": oauth_app.client_id,
                "client_secret": oauth_app.client_secret,
                "redirect_uri": oauth_app.redirect_uri
            }
            
            if platform == "pinterest":
                provider = PinterestProvider(credentials)
                token_data = provider.exchange_code_for_tokens(code)
            elif platform == "linkedin":
                provider = LinkedInProvider(credentials)
                token_data = provider.exchange_code_for_tokens(code)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Platform {platform} not supported"
                )
        
        # Encrypt tokens
        encrypted_access = encrypt_token(token_data["access_token"])
        encrypted_refresh = None
        if token_data.get("refresh_token"):
            encrypted_refresh = encrypt_token(token_data["refresh_token"])
        
        # Save integration
        integration = Integration(
            tenant_id=tenant_id,
            oauth_app_id=oauth_app.id,
            platform=platform,
            account_name=token_data.get("account_name"),
            account_id=token_data.get("account_id"),
            profile_picture=token_data.get("profile_image"),
            access_token=encrypted_access,
            refresh_token=encrypted_refresh,
            token_type=token_data.get("token_type", "Bearer"),
            expires_at=token_data.get("expires_at")
        )
        
        db.add(integration)
        db.commit()
        
        return {
            "success": True, 
            "account": token_data.get("account_name"),
            "mock_mode": is_mock
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth exchange failed: {str(e)}"
        )


@router.get("/test/status")
def test_oauth_status():
    """Check OAuth test mode status and available test credentials."""
    from core.test_oauth import TEST_OAUTH_APPS, validate_test_credentials
    
    status = {
        "mock_mode_globally_enabled": is_test_mode(),
        "platforms": {}
    }
    
    for platform in ["pinterest", "linkedin", "x"]:
        has_real_creds = validate_test_credentials(platform)
        config = TEST_OAUTH_APPS.get(platform, {})
        
        status["platforms"][platform] = {
            "has_credentials": has_real_creds,
            "client_id_prefix": config.get("client_id", "")[:10] + "..." if config.get("client_id") else None,
            "can_test_with_mock": True
        }
    
    return status