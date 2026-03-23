"""Facebook provider implementation.

Facebook uses Meta's Graph API.
Docs: https://developers.facebook.com/docs/graph-api
"""
from typing import Dict, Optional
import requests
from .base import SocialProvider


class FacebookProvider(SocialProvider):
    """Facebook Pages provider via Meta Graph API."""

    identifier = 'facebook'
    name = 'Facebook'
    oauth_version = 'oauth2'
    editor = 'html'

    max_characters = 63206  # Posts
    max_media = 10  # Images in albums
    max_video_duration = 14400  # 4 hours

    authorization_url = 'https://www.facebook.com/v18.0/dialog/oauth'
    token_url = 'https://graph.facebook.com/v18.0/oauth/access_token'
    api_base_url = 'https://graph.facebook.com/v18.0'

    scopes = [
        'pages_manage_posts',
        'pages_read_engagement',
        'pages_manage_engagement',
        'public_profile',
    ]

    def exchange_code_for_tokens(self, code: str) -> Dict:
        """Exchange authorization code for tokens."""
        from datetime import datetime, timedelta

        url = f'{self.api_base_url}/oauth/access_token'
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'code': code
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        access_token = data.get('access_token')
        expires_in = data.get('expires_in', 5184000)
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        # Get long-lived token (60 days)
        long_lived = self._get_long_lived_token(access_token)

        # Get page info
        page_info = self._get_default_page(long_lived.get('access_token', access_token))

        return {
            'access_token': long_lived.get('access_token', access_token),
            'refresh_token': None,  # Facebook doesn't use refresh tokens
            'token_type': 'Bearer',
            'expires_at': expires_at,
            'account_id': page_info.get('id'),
            'account_name': page_info.get('name'),
            'profile_image': None
        }

    def _get_long_lived_token(self, short_token: str) -> Dict:
        """Exchange for long-lived token (60 days)."""
        url = f'{self.api_base_url}/oauth/access_token'
        params = {
            'grant_type': 'fb_exchange_token',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'fb_exchange_token': short_token
        }
        response = requests.get(url, params=params)
        if response.ok:
            return response.json()
        return {'access_token': short_token}

    def _get_default_page(self, access_token: str) -> Dict:
        """Get the first managed Facebook Page."""
        url = f'{self.api_base_url}/me/accounts'
        params = {'access_token': access_token}
        response = requests.get(url, params=params)
        if response.ok:
            pages = response.json().get('data', [])
            if pages:
                return pages[0]
        # Fallback to user profile
        user_url = f'{self.api_base_url}/me'
        user_params = {'fields': 'id,name', 'access_token': access_token}
        user_response = requests.get(user_url, params=user_params)
        if user_response.ok:
            return user_response.json()
        return {'id': 'unknown', 'name': 'Unknown'}

    def post(self, content: str, access_token: str, media_urls: Optional[list] = None,
             page_id: Optional[str] = None, **kwargs) -> Dict:
        """Create a Facebook post.

        Args:
            content: Post content
            access_token: Page access token
            media_urls: List of image URLs to attach
            page_id: Specific page ID (uses default if not provided)
        """
        if page_id is None:
            page_info = self._get_default_page(access_token)
            page_id = page_info.get('id')

        url = f'{self.api_base_url}/{page_id}/feed'

        data = {'message': content[:63206], 'access_token': access_token}

        # Attach media as link or photo
        if media_urls and len(media_urls) > 0:
            # For single image, use photo endpoint
            if len(media_urls) == 1:
                photo_url = f'{self.api_base_url}/{page_id}/photos'
                photo_data = {
                    'url': media_urls[0],
                    'caption': content[:63206],
                    'access_token': access_token
                }
                response = requests.post(photo_url, data=photo_data)
                response.raise_for_status()
                result = response.json()
                post_id = result.get('post_id')
                return {
                    'post_id': post_id,
                    'url': f'https://www.facebook.com/{page_id}/posts/{post_id}' if post_id else None,
                    'platform_response': result
                }
            else:
                # Multiple images: create an album
                data['attached_media'] = str([
                    {'media_fbid': self._upload_photo(page_id, url, token) for url in media_urls}
                ])

        response = requests.post(url, data=data)
        response.raise_for_status()
        result = response.json()

        post_id = result.get('id')
        return {
            'post_id': post_id,
            'url': f'https://www.facebook.com/{page_id}/posts/{post_id}' if post_id else None,
            'platform_response': result
        }

    def _upload_photo(self, page_id: str, access_token: str) -> str:
        """Upload a photo and return the FB media ID."""
        # Placeholder - actual implementation would upload to page
        return ''

    def get_pages(self, access_token: str) -> list:
        """Get all Facebook Pages managed by this account."""
        url = f'{self.api_base_url}/me/accounts'
        params = {'access_token': access_token}
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get('data', [])

    def get_profile(self, access_token: str, page_id: Optional[str] = None) -> Dict:
        """Get Page profile information."""
        if page_id is None:
            page_info = self._get_default_page(access_token)
            page_id = page_info.get('id')

        url = f'{self.api_base_url}/{page_id}'
        params = {
            'fields': 'id,name,fan_count,followers_count,about,cover,picture',
            'access_token': access_token
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
