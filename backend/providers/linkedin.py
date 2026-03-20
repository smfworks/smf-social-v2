"""LinkedIn provider implementation.

LinkedIn uses OAuth 2.0 with a more complex API.
Docs: https://learn.microsoft.com/en-us/linkedin/
"""
from typing import Dict, Optional
import requests
from .base import SocialProvider

class LinkedInProvider(SocialProvider):
    """LinkedIn social media provider."""
    
    identifier = 'linkedin'
    name = 'LinkedIn'
    oauth_version = 'oauth2'
    editor = 'normal'
    
    # LinkedIn limits
    max_characters = 3000  # Posts
    max_media = 9  # Images in carousel
    
    # OAuth endpoints (LinkedIn Marketing API)
    authorization_url = 'https://www.linkedin.com/oauth/v2/authorization'
    token_url = 'https://www.linkedin.com/oauth/v2/accessToken'
    api_base_url = 'https://api.linkedin.com/v2'
    
    # Scopes (w_compliance required for posting)
    scopes = [
        'openid',
        'profile',
        'email',
        'w_member_social',  # Post on behalf of user
        'r_basicprofile',
        'r_liteprofile',
        'w_organization_social'  # For company pages
    ]
    
    def exchange_code_for_tokens(self, code: str) -> Dict:
        """Exchange authorization code for tokens.
        
        LinkedIn-specific implementation.
        """
        import urllib.parse
        from datetime import datetime, timedelta
        
        payload = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': self.redirect_uri
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
        
        # Get user info with OpenID Connect
        access_token = data.get('access_token')
        user_info = self._get_user_info(access_token)
        
        expires_in = data.get('expires_in', 5184000)  # LinkedIn: ~60 days
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        return {
            'access_token': access_token,
            'refresh_token': data.get('refresh_token'),  # May not be provided
            'token_type': data.get('token_type', 'Bearer'),
            'expires_at': expires_at,
            'scope': data.get('scope', ''),
            'account_id': user_info.get('sub'),  # OpenID subject
            'account_name': user_info.get('name'),
            'profile_picture': user_info.get('picture')
        }
    
    def _get_user_info(self, access_token: str) -> Dict:
        """Fetch LinkedIn user info via OpenID Connect."""
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        response = requests.get(
            'https://api.linkedin.com/v2/userinfo',
            headers=headers
        )
        response.raise_for_status()
        
        return response.json()
    
    def post(self, content: str, access_token: str, media_urls: Optional[list] = None,
             visibility: str = 'PUBLIC', **kwargs) -> Dict:
        """Create a LinkedIn post.
        
        Args:
            content: Post content
            access_token: OAuth access token
            media_urls: Optional media URLs
            visibility: 'PUBLIC' or 'CONNECTIONS'
            
        Returns:
            Dict with post_id, url
            
        Note: LinkedIn posting is complex. This is simplified version.
        Full implementation requires UGC posts API.
        """
        # LinkedIn uses UGC (User Generated Content) Posts API
        # This requires more complex implementation
        
        # For now, raise NotImplementedError with guidance
        raise NotImplementedError(
            "LinkedIn posting requires UGC Posts API implementation. "
            "See: https://learn.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/posts-api "
            "Requires: w_member_social scope, asset uploads, and specific JSON-LD format."
        )
    
    def get_profile(self, access_token: str) -> Dict:
        """Get LinkedIn profile information."""
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        response = requests.get(
            f'{self.api_base_url}/me',
            headers=headers
        )
        response.raise_for_status()
        
        return response.json()
