"""Post management routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional

from core.database import get_db
from core.security import decrypt_token
from models.sqlite_database import Post, Integration

router = APIRouter(prefix="/posts", tags=["posts"])

SUPPORTED_PLATFORMS = ["linkedin", "x", "instagram", "facebook", "tiktok"]


def get_provider_for_platform(platform: str):
    """Import and return the provider class for a platform."""
    if platform == "linkedin":
        from providers.linkedin import LinkedInProvider
        return LinkedInProvider
    elif platform == "x":
        from providers.x import XProvider
        return XProvider
    elif platform == "instagram":
        from providers.instagram import InstagramProvider
        return InstagramProvider
    elif platform == "facebook":
        from providers.facebook import FacebookProvider
        return FacebookProvider
    elif platform == "tiktok":
        from providers.tiktok import TikTokProvider
        return TikTokProvider
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Platform '{platform}' not supported"
        )


@router.post("/")
def create_post(
    tenant_id: str,
    content: str,
    integration_id: str,
    scheduled_for: Optional[datetime] = None,
    media_urls: Optional[List[str]] = None,
    db: Session = Depends(get_db)
):
    """Create a new post (scheduled or draft)."""
    # Verify integration exists
    integration = db.query(Integration).filter(
        Integration.id == integration_id,
        Integration.tenant_id == tenant_id,
        Integration.is_active == True
    ).first()

    if not integration:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Integration not found"
        )

    # Create post
    post = Post(
        tenant_id=tenant_id,
        integration_id=integration_id,
        content=content,
        media_urls=media_urls or [],
        scheduled_for=scheduled_for,
        status="scheduled" if scheduled_for else "draft"
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    return {
        "id": post.id,
        "status": post.status,
        "scheduled_for": post.scheduled_for.isoformat() if post.scheduled_for else None
    }


@router.get("/")
def list_posts(
    tenant_id: str,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List posts for a tenant."""
    query = db.query(Post).filter(Post.tenant_id == tenant_id)

    if status:
        query = query.filter(Post.status == status)

    posts = query.order_by(Post.created_at.desc()).all()

    return [
        {
            "id": post.id,
            "content": post.content,
            "platform": post.integration.platform if post.integration else None,
            "status": post.status,
            "scheduled_for": post.scheduled_for.isoformat() if post.scheduled_for else None,
            "published_at": post.published_at.isoformat() if post.published_at else None,
            "created_at": post.created_at.isoformat() if post.created_at else None
        }
        for post in posts
    ]


@router.post("/{post_id}/publish")
def publish_post(
    post_id: str,
    tenant_id: str,
    db: Session = Depends(get_db)
):
    """Publish a post immediately."""
    post = db.query(Post).filter(
        Post.id == post_id,
        Post.tenant_id == tenant_id
    ).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    if post.status == "published":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post already published"
        )

    # Get integration
    integration = post.integration
    if not integration or not integration.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Integration not available"
        )

    platform = integration.platform

    # Decrypt token
    access_token = decrypt_token(integration.access_token)
    
    # For X (OAuth 1.0a), we also need the token secret stored in refresh_token
    oauth_token_secret = None
    if platform == "x" and integration.refresh_token:
        oauth_token_secret = decrypt_token(integration.refresh_token)

    # Get OAuth app for provider
    oauth_app = integration.oauth_app

    # Build credentials
    credentials = {
        "client_id": oauth_app.client_id if oauth_app else None,
        "client_secret": oauth_app.client_secret if oauth_app else None,
        "redirect_uri": oauth_app.redirect_uri if oauth_app else None,
    }

    # Post to platform
    try:
        ProviderClass = get_provider_for_platform(platform)
        provider = ProviderClass(credentials)
        
        # Build post kwargs
        post_kwargs = {
            "content": post.content,
            "access_token": access_token,
            "media_urls": post.media_urls
        }
        
        # Add OAuth 1.0a token secret for X
        if platform == "x" and oauth_token_secret:
            post_kwargs["oauth_token_secret"] = oauth_token_secret
        
        result = provider.post(**post_kwargs)

        # Update post
        post.status = "published"
        post.published_at = datetime.utcnow()
        post.platform_post_id = result.get("post_id")
        post.platform_url = result.get("url")
        post.platform_response = result.get("platform_response")

        # Update last used
        integration.last_used_at = datetime.utcnow()

        db.commit()

        return {
            "success": True,
            "post_id": post.id,
            "platform_url": post.platform_url
        }

    except HTTPException:
        raise
    except Exception as e:
        post.status = "failed"
        post.error_message = str(e)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to publish: {str(e)}"
        )


@router.delete("/{post_id}")
def delete_post(
    post_id: str,
    tenant_id: str,
    db: Session = Depends(get_db)
):
    """Delete a scheduled post."""
    post = db.query(Post).filter(
        Post.id == post_id,
        Post.tenant_id == tenant_id
    ).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    if post.status == "published":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete published post"
        )

    db.delete(post)
    db.commit()

    return {"success": True}
