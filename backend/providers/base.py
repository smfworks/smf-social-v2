"""Base class for all social media providers.

All platform implementations must inherit from this class.
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import requests
import secrets

class SocialProvider(ABC):
    """Abstract base class for social media platforms."""
    
    # Platform identifier (override in subclass)
    identifier: str = None
    name: str = None
    
    # OAuth version: 'oauth2' or 'oauth1'
    oauth_version: str = 'oauth2'
    
    # Editor type: 'normal', 'markdown', 'html'
    editor: str = 'normal'
    
    # Rate limiting
    max_characters: int = 2000
    max_media: int = 4
    max_video_duration: int = 60  # seconds
    
    # API endpoints (override in subclass)
    authorization_url: str = None
    token_url: str = None
    api_base_url: str = None
    
    # Required OAuth scopes
    scopes: list = []
    
    def __init__(self, oauth_app_credentials: Dict):
        """Initialize provider with OAuth app credentials.
        
        Args:
            oauth_app_credentials: Dict with client_id, client_secret, redirect_uri
        """
        self.client_id = oauth_app_credentials.get('client_id')
        self.client_secret = oauth_app_credentials.get('client_secret')
        self.redirect_uri = oauth_app_credentials.get('redirect_uri')
    
    # ============================
    # OAuth Flow (OAuth 2.0)
    # ============================
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """Generate OAuth authorization URL.
        
        Args:
            state: Random state string for CSRF protection
            
        Returns:
            Full authorization URL
        """
        if self.oauth_version == 'oauth2':
            return self._get_oauth2_authorization_url(state)
        else:
            return self._get_oauth1_authorization_url(state)
    
    def _get_oauth2_authorization_url(self, state: Optional[str] = None) -> str:
        """Generate OAuth 2.0 authorization URL."""
        import urllib.parse
        
        if state is None:
            state = secrets.token_urlsafe(32)
        
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': ' '.join(self.scopes),
            'state': state
        }
        
        query_string = urllib.parse.urlencode(params)
        return f"{self.authorization_url}?{query_string}"
    
    @abstractmethod
    def _get_oauth1_authorization_url(self, state: Optional[str] = None) -> str:
        """Generate OAuth 1.0a authorization URL (platform-specific)."""
        pass
    
    def exchange_code_for_tokens(self, code: str) -> Dict:
        """Exchange authorization code for access/refresh tokens.
        
        Args:
            code: Authorization code from callback
            
        Returns:
            Dict with access_token, refresh_token, expires_at, etc.
        """
        if self.oauth_version == 'oauth2':
            return self._exchange_oauth2_code(code)
        else:
            return self._exchange_oauth1_code(code)
    
    def _exchange_oauth2_code(self, code: str) -> Dict:
        """Exchange OAuth 2.0 code for tokens."""
        import urllib.parse
        
        payload = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'code': code
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        response = requests.post(
            self.token_url,
            data=urllib.parse.urlencode(payload),
            headers=headers
        )
        response.raise_for_status()
        
        data = response.json()
        
        # Calculate expiration
        expires_in = data.get('expires_in', 3600)
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        return {
            'access_token': data.get('access_token'),
            'refresh_token': data.get('refresh_token'),
            'token_type': data.get('token_type', 'Bearer'),
            'expires_at': expires_at,
            'scope': data.get('scope', ''),
            'account_id': data.get('user_id'),  # platform-specific
            'account_name': data.get('username')  # platform-specific
        }
    
    @abstractmethod
    def _exchange_oauth1_code(self, code: str) -> Dict:
        """Exchange OAuth 1.0a code for tokens (platform-specific)."""
        pass
    
    def refresh_access_token(self, refresh_token: str) -> Dict:
        """Refresh expired access token.
        
        Args:
            refresh_token: Refresh token from original authorization
            
        Returns:
            Dict with new access_token, expires_at, etc.
        """
        if self.oauth_version == 'oauth1':
            raise NotImplementedError("OAuth 1.0a doesn't use refresh tokens")
        
        import urllib.parse
        
        payload = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        response = requests.post(
            self.token_url,
            data=urllib.parse.urlencode(payload),
            headers=headers
        )
        response.raise_for_status()
        
        data = response.json()
        
        expires_in = data.get('expires_in', 3600)
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        return {
            'access_token': data.get('access_token'),
            'refresh_token': data.get('refresh_token') or refresh_token,
            'expires_at': expires_at,
            'token_type': data.get('token_type', 'Bearer')
        }
    
    # ============================
    # Posting
    # ============================
    
    @abstractmethod
    def post(self, content: str, access_token: str, media_urls: Optional[list] = None, **kwargs) -> Dict:
        """Publish a post to the platform.
        
        Args:
            content: Post text content
            access_token: Valid access token
            media_urls: List of media URLs to attach
            **kwargs: Platform-specific parameters
            
        Returns:
            Dict with post_id, url, and platform response
        """
        pass
    
    def validate_content(self, content: str, media_urls: Optional[list] = None) -> Tuple[bool, str]:
        """Validate content before posting.
        
        Args:
            content: Post content
            media_urls: Media to attach
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(content) > self.max_characters:
            return False, f"Content exceeds {self.max_characters} characters"
        
        if media_urls and len(media_urls) > self.max_media:
            return False, f"Cannot attach more than {self.max_media} media items"
        
        return True, ""
    
    # ============================
    # Utility
    # ============================
    
    def make_api_request(self, method: str, endpoint: str, access_token: str, 
                        data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict:
        """Make authenticated API request.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            access_token: OAuth access token
            data: Request body data
            params: Query parameters
            
        Returns:
            Parsed JSON response
        """
        url = f"{self.api_base_url}{endpoint}"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=data,
            params=params
        )
        
        response.raise_for_status()
        return response.json()
    
    @classmethod
    def requires_user_auth(cls) -> bool:
        """Check if this provider requires end-user OAuth authorization."""
        return True
    
    @classmethod
    def supports_refresh(cls) -> bool:
        """Check if this provider supports token refresh."""
        return cls.oauth_version == 'oauth2'
