"""SQLite database models for SMF Social v2.

Single-tenant design with file-based storage.
No PostgreSQL required - just SQLite.
"""
from sqlalchemy import create_engine, Column, String, DateTime, Text, Boolean, ForeignKey, JSON, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import uuid
import os

Base = declarative_base()

class Tenant(Base):
    """Single tenant record for this deployment."""
    __tablename__ = 'tenants'
    
    # Single tenant per deployment
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    slug = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Settings stored as JSON
    settings = Column(JSON, default={})
    is_active = Column(Boolean, default=True)
    
    # Relationships
    oauth_apps = relationship("OAuthApp", back_populates="tenant", cascade="all, delete-orphan")
    integrations = relationship("Integration", back_populates="tenant", cascade="all, delete-orphan")
    posts = relationship("Post", back_populates="tenant", cascade="all, delete-orphan")
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")

class User(Base):
    """Admin users for this tenant."""
    __tablename__ = 'users'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey('tenants.id'), nullable=False)
    
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)  # bcrypt
    name = Column(String(255))
    is_admin = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    tenant = relationship("Tenant", back_populates="users")

class OAuthApp(Base):
    """OAuth app credentials for each platform.
    
    Customer creates their own app on each platform.
    """
    __tablename__ = 'oauth_apps'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey('tenants.id'), nullable=False)
    
    platform = Column(String(50), nullable=False)  # 'x', 'linkedin', 'instagram', 'facebook', 'tiktok'
    
    # OAuth credentials (encrypted)
    client_id = Column(String(500), nullable=False)
    client_secret = Column(Text, nullable=False)  # encrypted
    redirect_uri = Column(String(500), nullable=False)
    
    # OAuth endpoints
    authorization_url = Column(String(500))
    token_url = Column(String(500))
    
    scopes = Column(JSON, default=[])
    
    app_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    tenant = relationship("Tenant", back_populates="oauth_apps")

class Integration(Base):
    """Connected social account (user authorization)."""
    __tablename__ = 'integrations'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey('tenants.id'), nullable=False)
    oauth_app_id = Column(String(36), ForeignKey('oauth_apps.id'))
    
    platform = Column(String(50), nullable=False)
    account_name = Column(String(255))
    account_id = Column(String(255))
    profile_picture = Column(Text)
    
    # OAuth tokens (encrypted)
    access_token = Column(Text, nullable=False)  # encrypted
    refresh_token = Column(Text)  # encrypted
    token_type = Column(String(50), default='Bearer')
    expires_at = Column(DateTime)
    
    settings = Column(JSON, default={})  # platform-specific settings
    
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
    user_id = Column(String(36), ForeignKey('users.id'))  # who created it
    
    content = Column(Text, nullable=False)
    media_urls = Column(JSON, default=[])
    
    scheduled_for = Column(DateTime)
    published_at = Column(DateTime)
    
    status = Column(String(50), default='draft')  # draft, scheduled, publishing, published, failed
    error_message = Column(Text)
    
    platform_post_id = Column(String(255))
    platform_response = Column(JSON)
    platform_url = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    tenant = relationship("Tenant", back_populates="posts")
    integration = relationship("Integration", back_populates="posts")

class Media(Base):
    """Uploaded media assets."""
    __tablename__ = 'media'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey('tenants.id'), nullable=False)
    
    original_filename = Column(String(500))
    file_path = Column(Text)
    file_url = Column(Text)
    mime_type = Column(String(100))
    file_size = Column(Integer)
    
    platform_upload_status = Column(String(50), default='pending')
    platform_media_id = Column(String(255))
    
    width = Column(Integer)
    height = Column(Integer)
    duration = Column(String(50))
    
    created_at = Column(DateTime, default=datetime.utcnow)

# Database setup functions
def get_sqlite_engine(data_dir: str = "/data"):
    """Create SQLite engine."""
    os.makedirs(data_dir, exist_ok=True)
    db_path = os.path.join(data_dir, "smf_social.db")
    return create_engine(f"sqlite:///{db_path}", echo=False)

def init_sqlite_db(engine):
    """Initialize database tables."""
    Base.metadata.create_all(engine)

def get_sqlite_session(engine):
    """Get database session."""
    Session = sessionmaker(bind=engine)
    return Session()
