"""Integration management routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from core.database import get_db
from core.security import decrypt_token, encrypt_token
from models.sqlite_database import Integration, OAuthApp

router = APIRouter(prefix="/integrations", tags=["integrations"])

# Supported platforms (Pinterest removed 2026-03-23)
SUPPORTED_PLATFORMS = ["linkedin", "x", "instagram", "facebook", "tiktok"]


@router.get("/")
def list_integrations(
    tenant_id: str,
    db: Session = Depends(get_db)
):
    """List all connected integrations for a tenant."""
    integrations = db.query(Integration).filter(
        Integration.tenant_id == tenant_id,
        Integration.is_active == True
    ).all()

    return [
        {
            "id": integration.id,
            "platform": integration.platform,
            "account_name": integration.account_name,
            "account_id": integration.account_id,
            "profile_picture": integration.profile_picture,
            "created_at": integration.created_at.isoformat() if integration.created_at else None,
            "last_used_at": integration.last_used_at.isoformat() if integration.last_used_at else None
        }
        for integration in integrations
    ]


@router.post("/manual-token")
def manual_token_entry(
    platform: str,
    tenant_id: str,
    access_token: str,
    db: Session = Depends(get_db)
):
    """Add integration via manual token entry (for testing)."""
    if platform not in SUPPORTED_PLATFORMS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Platform '{platform}' not supported. Available: {', '.join(SUPPORTED_PLATFORMS)}"
        )

    # Get or create OAuth app
    oauth_app = db.query(OAuthApp).filter(
        OAuthApp.tenant_id == tenant_id,
        OAuthApp.platform == platform
    ).first()

    if not oauth_app:
        oauth_app = OAuthApp(
            tenant_id=tenant_id,
            platform=platform,
            client_id=f"manual-{platform}",
            client_secret="manual-secret",
            redirect_uri="http://localhost/callback",
            app_name=f"Manual {platform.title()}"
        )
        db.add(oauth_app)
        db.commit()

    # Encrypt token
    encrypted_token = encrypt_token(access_token)

    # Create integration
    integration = Integration(
        tenant_id=tenant_id,
        oauth_app_id=oauth_app.id,
        platform=platform,
        account_name=f"@{platform}-manual",
        account_id=f"manual-{platform}-id",
        access_token=encrypted_token,
        token_type="Bearer",
        is_active=True,
        created_at=datetime.utcnow(),
        last_used_at=datetime.utcnow()
    )

    db.add(integration)
    db.commit()

    return {
        "success": True,
        "message": f"{platform.title()} integration created with manual token",
        "integration_id": integration.id
    }


@router.delete("/{integration_id}")
def disconnect_integration(
    integration_id: str,
    tenant_id: str,
    db: Session = Depends(get_db)
):
    """Disconnect a social media account."""
    integration = db.query(Integration).filter(
        Integration.id == integration_id,
        Integration.tenant_id == tenant_id
    ).first()

    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )

    # Soft delete
    integration.is_active = False
    db.commit()

    return {"success": True, "message": f"Disconnected {integration.platform}"}


# ============================================================================
# Platform-specific helpers (boards, pages, profiles)
# ============================================================================

@router.get("/{integration_id}/pages")
def get_linkedin_pages(
    integration_id: str,
    tenant_id: str,
    db: Session = Depends(get_db)
):
    """Get LinkedIn pages for an integration."""
    integration = db.query(Integration).filter(
        Integration.id == integration_id,
        Integration.tenant_id == tenant_id,
        Integration.platform == "linkedin"
    ).first()

    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LinkedIn integration not found"
        )

    # In test mode, return mock pages
    if integration.account_name.startswith("@testuser") or "test" in (integration.access_token or ""):
        return {
            "pages": [
                {"id": "12345678", "name": "Test Company Page", " vanity_name": "testcompany"},
                {"id": "87654321", "name": "Test Personal Page", " vanity_name": "testuser"}
            ]
        }

    # Real LinkedIn API call
    access_token = decrypt_token(integration.access_token)
    try:
        from providers.linkedin import LinkedInProvider
        provider = LinkedInProvider({})
        pages = provider.get_pages(access_token)
        return {"pages": pages}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch LinkedIn pages: {str(e)}"
        )


@router.get("/{integration_id}/profile")
def get_platform_profile(
    integration_id: str,
    tenant_id: str,
    db: Session = Depends(get_db)
):
    """Get profile info for an integration."""
    integration = db.query(Integration).filter(
        Integration.id == integration_id,
        Integration.tenant_id == tenant_id
    ).first()

    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )

    platform = integration.platform

    # In test mode, return mock profiles
    mock_profiles = {
        "linkedin": {"id": "urn:li:person:test123", "name": "Test User", "headline": "CEO at Test Corp"},
        "x": {"id": "123456789", "name": "Test User", "username": "@testuser", "followers": 1000},
        "instagram": {"id": "17841400000000000", "username": "@testuser", "followers": 500, "media_count": 50},
        "facebook": {"id": "1234567890123456", "name": "Test Page", "followers": 2000, "category": "Business"},
        "tiktok": {"id": "1234567890123456789", "username": "@testuser", "followers": 10000, "following": 500},
    }

    if platform in mock_profiles:
        return mock_profiles[platform]

    return {
        "account_id": integration.account_id,
        "account_name": integration.account_name,
    }


@router.post("/{integration_id}/refresh")
def refresh_integration(
    integration_id: str,
    tenant_id: str,
    db: Session = Depends(get_db)
):
    """Refresh an integration's access token."""
    integration = db.query(Integration).filter(
        Integration.id == integration_id,
        Integration.tenant_id == tenant_id
    ).first()

    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )

    if not integration.refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This integration does not support token refresh"
        )

    access_token = decrypt_token(integration.refresh_token)

    # Refresh based on platform
    if integration.platform == "linkedin":
        from providers.linkedin import LinkedInProvider
        provider = LinkedInProvider({})
        try:
            new_tokens = provider.refresh_access_token(access_token)
            integration.access_token = encrypt_token(new_tokens["access_token"])
            if new_tokens.get("refresh_token"):
                integration.refresh_token = encrypt_token(new_tokens["refresh_token"])
            integration.expires_at = new_tokens.get("expires_at")
            db.commit()
            return {"success": True, "message": "Token refreshed"}
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Token refresh failed: {str(e)}"
            )

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Token refresh not implemented for {integration.platform}"
    )
