"""Pinterest provider implementation.

Pinterest uses OAuth 2.0 with a simple REST API.
Docs: https://developers.pinterest.com/docs/api/v5/
"""
from typing import Dict, Optional
import requests
from .base import SocialProvider

class PinterestProvider(SocialProvider):
    """Pinterest social media provider."""
    
    identifier = 'pinterest'
    name = 'Pinterest'
    oauth_version = 'oauth2'
    editor = 'normal'
    
    # Pinterest limits
    max_characters = 500
    max_media = 1  # Pinterest pins can have 1 image/video
    
    # OAuth endpoints
    authorization_url = 'https://www.pinterest.com/oauth/'
    token_url = 'https://api.pinterest.com/v5/oauth/token'
    api_base_url = 'https://api.pinterest.com/v5'
    
    # Scopes (Pinterest v5)
    scopes = [
        'boards:read',
        'boards:write', 
        'pins:read',
        'pins:write',
        'user_accounts:read'
    ]
    
    def exchange_code_for_tokens(self, code: str) -> Dict:
        """Exchange authorization code for tokens.
        
        Pinterest-specific implementation that fetches user info.
        """
        import urllib.parse
        
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
        
        # Get user info
        access_token = data.get('access_token')
        user_info = self._get_user_info(access_token)
        
        from datetime import datetime, timedelta
        expires_in = data.get('expires_in', 3600)
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        return {
            'access_token': access_token,
            'refresh_token': data.get('refresh_token'),
            'token_type': data.get('token_type', 'Bearer'),
            'expires_at': expires_at,
            'scope': data.get('scope', ''),
            'account_id': user_info.get('id'),
            'account_name': user_info.get('username'),
            'profile_picture': user_info.get('profile_image')
        }
    
    def _get_user_info(self, access_token: str) -> Dict:
        """Fetch Pinterest user account information."""
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        response = requests.get(
            f'{self.api_base_url}/user_account',
            headers=headers
        )
        response.raise_for_status()
        
        data = response.json()
        return {
            'id': data.get('id'),
            'username': data.get('username'),
            'profile_image': data.get('profile_image')
        }
    
    def post(self, content: str, access_token: str, media_urls: Optional[list] = None, 
             board_id: Optional[str] = None, link: Optional[str] = None, **kwargs) -> Dict:
        """Create a Pinterest Pin.
        
        Args:
            content: Pin description
            access_token: OAuth access token
            media_urls: List containing single image URL
            board_id: Pinterest board ID (required)
            link: URL to link from pin
            
        Returns:
            Dict with pin_id, url, and response data
        """
        if not board_id:
            raise ValueError("Pinterest requires a board_id to post pins")
        
        if not media_urls or len(media_urls) == 0:
            raise ValueError("Pinterest pins require an image")
        
        # Pinterest API v5 requires media upload first
        media_url = media_urls[0]
        
        # For now, assume media is already hosted at public URL
        # In production, you'd upload to Pinterest's CDN first
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'title': content[:100],  # Pinterest truncates titles
            'description': content,
            'board_id': board_id,
            'media_source': {
                'source_type': 'image_url',
                'url': media_url
            }
        }
        
        if link:
            payload['link'] = link
        
        response = requests.post(
            f'{self.api_base_url}/pins',
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        
        data = response.json()
        
        return {
            'post_id': data.get('id'),
            'url': data.get('link') or f"https://pinterest.com/pin/{data.get('id')}",
            'platform_response': data,
            'created_at': data.get('created_at')
        }
    
    def get_boards(self, access_token: str) -> list:
        """Get list of user's Pinterest boards.
        
        Useful for letting users select which board to post to.
        
        Args:
            access_token: OAuth access token
            
        Returns:
            List of board dicts with id, name, description
        """
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        response = requests.get(
            f'{self.api_base_url}/boards',
            headers=headers
        )
        response.raise_for_status()
        
        data = response.json()
        items = data.get('items', [])
        
        return [
            {
                'id': board.get('id'),
                'name': board.get('name'),
                'description': board.get('description'),
                'url': board.get('url')
            }
            for board in items
        ]
    
    def refresh_access_token(self, refresh_token: str) -> Dict:
        """Refresh Pinterest access token.
        
        Pinterest uses standard OAuth 2.0 refresh.
        """
        return super().refresh_access_token(refresh_token)
