from sqlalchemy import create_engine, Column, String, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import uuid

Base = declarative_base()

class Tenant(Base):
    """Multi-tenant customer isolation."""
    __tablename__ = 'tenants'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    slug = Column(String(50), unique=True, nullable=False)  # subdomain or identifier
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Settings stored as JSON
    settings = Column(JSON, default={})
    is_active = Column(Boolean, default=True)
    
    # Relationships
    oauth_apps = relationship("OAuthApp", back_populates="tenant", cascade="all, delete-orphan")
    integrations = relationship("Integration", back_populates="tenant", cascade="all, delete-orphan")
    posts = relationship("Post", back_populates="tenant", cascade="all, delete-orphan")

class OAuthApp(Base):
    """OAuth app credentials per tenant per platform.
    
    Customer creates their own app on X/LinkedIn/etc and stores credentials here.
    """
    __tablename__ = 'oauth_apps'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey('tenants.id'), nullable=False)
    
    # Platform identifier: 'x', 'linkedin', 'pinterest', etc.
    platform = Column(String(50), nullable=False)
    
    # OAuth credentials
    client_id = Column(String(500), nullable=False)
    client_secret = Column(Text, nullable=False)  # encrypted
    redirect_uri = Column(String(500), nullable=False)
    
    # OAuth endpoints (fetched from platform or stored)
    authorization_url = Column(String(500))
    token_url = Column(String(500))
    
    # Scopes requested
    scopes = Column(JSON, default=[])
    
    # Metadata
    app_name = Column(String(255))  # e.g., "SMF Works X App"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    tenant = relationship("Tenant", back_populates="oauth_apps")

class Integration(Base):
    """Connected social account (user authorization).
    
    Stores OAuth tokens after user authorizes the app.
    """
    __tablename__ = 'integrations'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey('tenants.id'), nullable=False)
    oauth_app_id = Column(String(36), ForeignKey('oauth_apps.id'))
    
    # Platform and account info
    platform = Column(String(50), nullable=False)
    account_name = Column(String(255))  # e.g., "@smfworks"
    account_id = Column(String(255))    # platform-specific ID
    profile_picture = Column(Text)       # URL to profile image
    
    # OAuth tokens (encrypted at application level)
    access_token = Column(Text, nullable=False)      # encrypted
    refresh_token = Column(Text)                      # encrypted
    token_type = Column(String(50), default='Bearer')
    expires_at = Column(DateTime)                   # when access_token expires
    
    # Platform-specific settings
    settings = Column(JSON, default={})  # e.g., Pinterest board ID
    
    # Status
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    tenant = relationship("Tenant", back_populates="integrations")
    posts = relationship("Post", back_populates="integration")

class Post(Base):
    """Scheduled or published social media post."""
    __tablename__ = 'posts'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey('tenants.id'), nullable=False)
    integration_id = Column(String(36), ForeignKey('integrations.id'), nullable=False)
    
    # Content
    content = Column(Text, nullable=False)        # post text
    media_urls = Column(JSON, default=[])         # array of image/video URLs
    
    # Scheduling
    scheduled_for = Column(DateTime)            # when to publish
    published_at = Column(DateTime)               # when actually published
    
    # Status
    status = Column(String(50), default='draft')  # draft, scheduled, publishing, published, failed
    error_message = Column(Text)                 # if failed
    
    # Platform response
    platform_post_id = Column(String(255))       # ID from platform (e.g., tweet ID)
    platform_response = Column(JSON)             # full API response
    platform_url = Column(Text)                  # public URL to published post
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    tenant = relationship("Tenant", back_populates="posts")
    integration = relationship("Integration", back_populates="posts")

class Media(Base):
    """Uploaded media assets."""
    __tablename__ = 'media'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey('tenants.id'), nullable=False)
    
    # File info
    original_filename = Column(String(500))
    file_path = Column(Text)                     # local storage path
    file_url = Column(Text)                      # CDN URL after upload
    mime_type = Column(String(100))
    file_size = Column(String(50))               # in bytes
    
    # Platform upload status
    platform_upload_status = Column(String(50), default='pending')  # pending, uploaded, failed
    platform_media_id = Column(String(255))      # ID from platform
    
    # Metadata
    width = Column(String(50))                   # for images
    height = Column(String(50))
    duration = Column(String(50))                # for videos
    
    created_at = Column(DateTime, default=datetime.utcnow)
