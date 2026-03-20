"""OAuth routes for social media platform connections."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional
import secrets

from core.database import get_db
from core.security import verify_token, encrypt_token
from models.sqlite_database import OAuthApp, Integration, Tenant
from providers.pinterest import PinterestProvider
from providers.linkedin import LinkedInProvider

router = APIRouter(prefix="/auth", tags=["auth"])

# Store state temporarily (use Redis in production)
oauth_states = {}

@router.get("/{platform}/connect")
def connect_platform(
    platform: str,
    tenant_id: str,
    db: Session = Depends(get_db)
):
    """Start OAuth flow for a platform."""
    # Get OAuth app credentials for tenant
    oauth_app = db.query(OAuthApp).filter(
        OAuthApp.tenant_id == tenant_id,
        OAuthApp.platform == platform,
        OAuthApp.is_active == True
    ).first()
    
    if not oauth_app:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No OAuth app configured for {platform}"
        )
    
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    oauth_states[state] = {
        "tenant_id": tenant_id,
        "platform": platform
    }
    
    # Get authorization URL
    credentials = {
        "client_id": oauth_app.client_id,
        "client_secret": oauth_app.client_secret,  # Need to decrypt
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
    
    return {"authorization_url": auth_url}


@router.get("/{platform}/callback")
def oauth_callback(
    platform: str,
    code: str,
    state: str,
    db: Session = Depends(get_db)
):
    """Handle OAuth callback from platform."""
    # Verify state
    if state not in oauth_states:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid state parameter"
        )
    
    state_data = oauth_states.pop(state)
    tenant_id = state_data["tenant_id"]
    
    # Get OAuth app
    oauth_app = db.query(OAuthApp).filter(
        OAuthApp.tenant_id == tenant_id,
        OAuthApp.platform == platform
    ).first()
    
    if not oauth_app:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OAuth app not found"
        )
    
    # Exchange code for tokens
    credentials = {
        "client_id": oauth_app.client_id,
        "client_secret": oauth_app.client_secret,
        "redirect_uri": oauth_app.redirect_uri
    }
    
    try:
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
        encrypted_refresh = encrypt_token(token_data["refresh_token"]) if token_data.get("refresh_token") else None
        
        # Save integration
        integration = Integration(
            tenant_id=tenant_id,
            oauth_app_id=oauth_app.id,
            platform=platform,
            account_name=token_data.get("account_name"),
            account_id=token_data.get("account_id"),
            profile_picture=token_data.get("profile_picture"),
            access_token=encrypted_access,
            refresh_token=encrypted_refresh,
            token_type=token_data.get("token_type", "Bearer"),
            expires_at=token_data.get("expires_at")
        )
        
        db.add(integration)
        db.commit()
        
        return {"success": True, "account": token_data.get("account_name")}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth exchange failed: {str(e)}"
        )
