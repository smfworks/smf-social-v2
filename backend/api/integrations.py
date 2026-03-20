"""Integration management routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from core.database import get_db
from core.security import decrypt_token, encrypt_token
from models.sqlite_database import Integration, OAuthApp

router = APIRouter(prefix="/integrations", tags=["integrations"])

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

@router.get("/{integration_id}/boards")
def get_pinterest_boards(
    integration_id: str,
    tenant_id: str,
    db: Session = Depends(get_db)
):
    """Get Pinterest boards for an integration."""
    integration = db.query(Integration).filter(
        Integration.id == integration_id,
        Integration.tenant_id == tenant_id,
        Integration.platform == "pinterest"
    ).first()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pinterest integration not found"
        )
    
    # Decrypt token
    access_token = decrypt_token(integration.access_token)
    
    # Get boards from Pinterest
    from providers.pinterest import PinterestProvider
    provider = PinterestProvider({})  # Credentials not needed for this call
    
    try:
        boards = provider.get_boards(access_token)
        return {"boards": boards}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch boards: {str(e)}"
        )
