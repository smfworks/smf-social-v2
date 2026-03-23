"""TikTok provider implementation.

TikTok uses OAuth 2.0 with client_key (not client_id).
Docs: https://developers.tiktok.com/doc/login-kit-web
"""
from typing import Dict, Optional
import requests
from .base import SocialProvider


class TikTokProvider(SocialProvider):
    """TikTok social media provider."""

    identifier = 'tiktok'
    name = 'TikTok'
    oauth_version = 'oauth2'
    editor = 'normal'

    max_characters = 2200
    max_media = 1  # One video per post
    max_video_duration = 180  # 3 minutes (can extend to 10 min with special approval)

    authorization_url = 'https://www.tiktok.com/v2/auth/authorize/'
    token_url = 'https://open.tiktokapis.com/v2/oauth/token/'
    api_base_url = 'https://open.tiktokapis.com/v2'

    scopes = [
        'user.info.basic',
        'video.upload',
        'video.publish',
        'video.publish谦',
    ]

    def exchange_code_for_tokens(self, code: str) -> Dict:
        """Exchange authorization code for tokens."""
        import urllib.parse
        from datetime import datetime, timedelta

        payload = {
            'grant_type': 'authorization_code',
            'client_key': self.client_id,  # TikTok uses client_key
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

        expires_in = data.get('expires_in', 86400)  # TikTok: 24 hours
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        return {
            'access_token': data.get('access_token'),
            'refresh_token': data.get('refresh_token'),
            'open_id': data.get('open_id'),
            'token_type': data.get('token_type', 'Bearer'),
            'expires_at': expires_at,
            'account_id': data.get('open_id'),
            'account_name': '@user',  # TikTok returns open_id, not username
            'profile_image': None
        }

    def refresh_access_token(self, refresh_token: str) -> Dict:
        """Refresh TikTok access token (expires in 24h)."""
        import urllib.parse
        from datetime import datetime, timedelta

        payload = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_key': self.client_id,
            'client_secret': self.client_secret
        }

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        response = requests.post(
            self.token_url,
            data=urllib.parse.urlencode(payload),
            headers=headers
        )
        response.raise_for_status()
        data = response.json()

        expires_in = data.get('expires_in', 86400)
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        return {
            'access_token': data.get('access_token'),
            'refresh_token': data.get('refresh_token'),
            'expires_at': expires_at,
        }

    def post(self, content: str, access_token: str, media_urls: Optional[list] = None,
             title: Optional[str] = None, **kwargs) -> Dict:
        """Create a TikTok video post.

        TikTok requires video to be uploaded first, then published.
        This is a 3-step process:
        1. Initialize upload session
        2. Upload video bytes
        3. Publish

        For now, this raises NotImplementedError as video upload
        requires handling binary data. Use the video.publish.external.query
        endpoint for URL-based posts.

        Args:
            content: Post description/caption
            access_token: OAuth access token
            media_urls: Video URL (must be publicly accessible MP4)
            title: Video title

        Returns:
            Dict with post_id, url
        """
        import urllib.parse

        if not media_urls or len(media_urls) == 0:
            raise NotImplementedError(
                "TikTok requires a video. Provide media_urls with a public MP4 URL. "
                "Note: TikTok does not support text-only posts."
            )

        video_url = media_urls[0]

        # Use TikTok's video.publish.external.query for URL-based posting
        # This allows posting a video from a public URL without uploading bytes
        url = f'{self.api_base_url}/video/publish/external/query/'

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        # Title defaults to content if not provided
        post_title = title or content[:2200]

        data = {
            'source': 'SOURCE_TYPE_URL',
            'video_url': video_url,
            'title': post_title,
            'privacy_level': 'SELF_ONLY',  # or 'PUBLIC', 'FOLLOWERS_ONLY'
            'disable_comment': False,
            'disable_share': False,
        }

        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        result = response.json()

        post_id = result.get('video_id')
        return {
            'post_id': post_id,
            'url': f'https://www.tiktok.com/@user/video/{post_id}' if post_id else None,
            'platform_response': result
        }

    def get_profile(self, access_token: str) -> Dict:
        """Get TikTok user profile."""
        url = f'{self.api_base_url}/user/info/'
        headers = {'Authorization': f'Bearer {access_token}'}
        params = {'fields': 'open_id,union_id,username,display_name,avatar_url,bio_description,profile_deep_link'}

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get('data', {})

    def get_video_list(self, access_token: str, max_count: int = 20) -> Dict:
        """Get user's video list."""
        url = f'{self.api_base_url}/video/list/'
        headers = {'Authorization': f'Bearer {access_token}'}
        params = {'max_count': max_count}

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    def validate_content(self, content: str, media_urls: Optional[list] = None) -> tuple:
        """Validate TikTok post content.

        TikTok requires:
        - Caption: 0-2200 characters
        - At least one video
        """
        if len(content) > self.max_characters:
            return False, f"Caption exceeds {self.max_characters} characters"

        if not media_urls or len(media_urls) == 0:
            return False, "TikTok requires at least one video"

        return True, ""
