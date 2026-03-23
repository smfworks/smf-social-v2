"""Instagram provider implementation.

Instagram uses Meta's Graph API (same as Facebook).
Docs: https://developers.facebook.com/docs/instagram-api
"""
from typing import Dict, Optional
import requests
from .base import SocialProvider


class InstagramProvider(SocialProvider):
    """Instagram social media provider via Meta Graph API."""

    identifier = 'instagram'
    name = 'Instagram'
    oauth_version = 'oauth2'
    editor = 'normal'

    max_characters = 2200
    max_media = 1  # Feed posts: 1 image/video per post
    max_video_duration = 60  # seconds (Feed video)

    authorization_url = 'https://api.instagram.com/oauth/authorize'
    token_url = 'https://api.instagram.com/oauth/access_token'
    api_base_url = 'https://graph.instagram.com'

    scopes = ['user_profile', 'user_media']

    def exchange_code_for_tokens(self, code: str) -> Dict:
        """Exchange authorization code for tokens."""
        import urllib.parse
        from datetime import datetime, timedelta

        payload = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'code': code
        }

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        response = requests.post(
            self.token_url,
            data=urllib.parse.urlencode(payload),
            headers=headers
        )
        response.raise_for_status()
        data = response.json()

        expires_in = data.get('expires_in', 5184000)
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        # Get long-lived token
        long_lived = self._exchange_for_long_lived_token(data.get('access_token'))

        return {
            'access_token': long_lived.get('access_token', data.get('access_token')),
            'refresh_token': data.get('refresh_token'),
            'token_type': 'Bearer',
            'expires_at': expires_at,
            'account_id': data.get('user_id'),
            'account_name': f'@{data.get("username", "user")}',
            'profile_image': None
        }

    def _exchange_for_long_lived_token(self, short_token: str) -> Dict:
        """Exchange short-lived token for long-lived token (60 days)."""
        url = 'https://graph.facebook.com/v18.0/oauth/access_token'
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

    def post(self, content: str, access_token: str, media_urls: Optional[list] = None,
              caption: Optional[str] = None, **kwargs) -> Dict:
        """Create an Instagram post.

        Instagram requires a 2-step process:
        1. Create a media container (upload image/video)
        2. Publish the container

        For simplicity this implements image posts via media container.
        """
        import uuid

        caption = caption or content
        ig_user_id = self._get_ig_user_id(access_token)

        # If media URLs provided, create image media container
        if media_urls and len(media_urls) > 0:
            media_url = media_urls[0]

            # Step 1: Create media container
            container_url = f'{self.api_base_url}/v18.0/{ig_user_id}/media'
            container_data = {
                'image_url': media_url,
                'caption': caption[:2200],
            }

            container_response = requests.post(
                container_url,
                params={'access_token': access_token},
                json=container_data
            )
            container_response.raise_for_status()
            container_id = container_response.json().get('id')

            # Step 2: Publish media container
            publish_url = f'{self.api_base_url}/v18.0/{ig_user_id}/media_publish'
            publish_data = {
                'creation_id': container_id,
                'access_token': access_token
            }

            publish_response = requests.post(publish_url, json=publish_data)
            publish_response.raise_for_status()
            result = publish_response.json()

            post_id = result.get('id')
            return {
                'post_id': post_id,
                'url': f'https://www.instagram.com/p/{post_id}/',
                'platform_response': result
            }

        # Text-only post (carousels not supported natively on personal accounts)
        raise NotImplementedError(
            "Instagram text-only posts require a Business/Creator account "
            "with Content Publishing API access. "
            "Media posts require image_url or media_urls parameter."
        )

    def _get_ig_user_id(self, access_token: str) -> str:
        """Get Instagram Business Account ID from access token."""
        # Get Facebook Page linked to Instagram
        url = f'{self.api_base_url}/me/accounts'
        params = {'access_token': access_token}
        response = requests.get(url, params=params)

        if response.ok:
            pages = response.json().get('data', [])
            if pages:
                page_id = pages[0]['id']
                # Get Instagram account linked to this page
                ig_url = f'https://graph.facebook.com/v18.0/{page_id}'
                ig_params = {
                    'fields': 'instagram_business_account',
                    'access_token': access_token
                }
                ig_response = requests.get(ig_url, params=ig_params)
                if ig_response.ok:
                    ig_data = ig_response.json()
                    if 'instagram_business_account' in ig_data:
                        return ig_data['instagram_business_account']['id']

        # Fallback: try to get user info directly
        url = f'{self.api_base_url}/me'
        params = {'fields': 'id,username', 'access_token': access_token}
        response = requests.get(url, params=params)
        if response.ok:
            data = response.json()
            return data.get('id', 'unknown')

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not find Instagram Business Account. "
                   "Ensure your Instagram is linked to a Facebook Page."
        )

    def get_profile(self, access_token: str) -> Dict:
        """Get Instagram Business account profile."""
        ig_user_id = self._get_ig_user_id(access_token)
        url = f'{self.api_base_url}/v18.0/{ig_user_id}'
        params = {
            'fields': 'id,username,name,media_count,followers_count,follows_count,biography,website',
            'access_token': access_token
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_media(self, access_token: str, limit: int = 25) -> Dict:
        """Get recent media posts."""
        ig_user_id = self._get_ig_user_id(access_token)
        url = f'{self.api_base_url}/v18.0/{ig_user_id}/media'
        params = {
            'fields': 'id,caption,media_type,media_url,thumbnail_url,timestamp,permalink',
            'limit': limit,
            'access_token': access_token
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
