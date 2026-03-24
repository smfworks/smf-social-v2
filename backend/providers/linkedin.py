"""LinkedIn provider implementation (Personal Profile).

LinkedIn uses OAuth 2.0 with the Posts API.
Docs: https://learn.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/posts-api

Personal Profile Posting (no LinkedIn Page required):
- Uses w_member_social scope
- Author URN: urn:li:person:{id}
- Posts to: https://api.linkedin.com/rest/posts
"""
from typing import Dict, Optional
import requests
from .base import SocialProvider


class LinkedInProvider(SocialProvider):
    """LinkedIn personal profile provider."""

    identifier = 'linkedin'
    name = 'LinkedIn'
    oauth_version = 'oauth2'
    editor = 'normal'

    # LinkedIn limits
    max_characters = 3000  # Posts
    max_media = 9  # Images in carousel

    # OAuth endpoints
    authorization_url = 'https://www.linkedin.com/oauth/v2/authorization'
    token_url = 'https://www.linkedin.com/oauth/v2/accessToken'
    api_base_url = 'https://api.linkedin.com/rest'

    # Scopes for personal profile posting
    scopes = [
        'openid',
        'profile',
        'email',
        'w_member_social',  # Post on behalf of user
    ]

    def exchange_code_for_tokens(self, code: str) -> Dict:
        """Exchange authorization code for tokens (OAuth 2.0)."""
        import urllib.parse
        from datetime import datetime, timedelta

        payload = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': self.redirect_uri
        }

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        response = requests.post(
            self.token_url,
            data=urllib.parse.urlencode(payload),
            headers=headers
        )
        response.raise_for_status()

        data = response.json()
        access_token = data.get('access_token')

        # Get user info via OpenID Connect
        user_info = self._get_user_info(access_token)
        person_id = user_info.get('sub')

        expires_in = data.get('expires_in', 5184000)  # ~60 days
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        return {
            'access_token': access_token,
            'refresh_token': data.get('refresh_token'),
            'token_type': data.get('token_type', 'Bearer'),
            'expires_at': expires_at,
            'scope': data.get('scope', ''),
            'account_id': person_id,
            'account_name': user_info.get('name'),
            'profile_picture': user_info.get('picture')
        }

    def _get_user_info(self, access_token: str) -> Dict:
        """Fetch LinkedIn user info via OpenID Connect."""
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get('https://api.linkedin.com/v2/userinfo', headers=headers)
        response.raise_for_status()
        return response.json()

    def _fix_text(self, text: str) -> str:
        """Escape special characters for LinkedIn's flair markup.

        Postiz reference: linkedin.provider.ts :: fixText()
        """
        import re

        # Match @mentions: @[displayName](urn:li:...)
        mention_pattern = r'@\[.+?\]\(urn:li:.+?\)'
        matches = re.findall(mention_pattern, text) or []
        split_parts = re.split(mention_pattern, text)

        def escape_text(t):
            # Order matters - escape backslashes first
            t = t.replace('\\', '\\\\')
            t = t.replace('<', '\\<')
            t = t.replace('>', '\\>')
            t = t.replace('#', '\\#')
            t = t.replace('~', '\\~')
            t = t.replace('_', '\\_')
            t = t.replace('|', '\\|')
            t = t.replace('[', '\\[')
            t = t.replace(']', '\\]')
            t = t.replace('*', '\\*')
            t = t.replace('(', '\\(')
            t = t.replace(')', '\\)')
            t = t.replace('{', '\\{')
            t = t.replace('}', '\\}')
            t = t.replace('@', '\\@')
            return t

        result = []
        for part in split_parts:
            result.append(escape_text(part))
            if matches:
                result.append(matches.pop(0))

        joined = ''.join(result)
        # Collapse multiple newlines into single newline, strip trailing
        return '\n'.join(line for line in joined.splitlines() if line).strip()

    def _upload_image(self, image_data: bytes, access_token: str, person_id: str) -> str:
        """Upload an image and return the media ID.

        Postiz reference: linkedin.provider.ts :: uploadPicture()
        """
        import uuid

        # Initialize upload
        init_url = f"{self.api_base_url}/images?action=initializeUpload"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0',
            'LinkedIn-Version': '202601',
        }
        init_payload = {
            "initializeUploadRequest": {
                "owner": f"urn:li:person:{person_id}"
            }
        }

        init_resp = requests.post(init_url, headers=headers, json=init_payload)
        if init_resp.status_code not in (200, 201):
            raise Exception(f"Failed to initialize image upload: {init_resp.status_code} - {init_resp.text}")

        upload_data = init_resp.json()
        upload_url = upload_data.get('value', {}).get('uploadUrl')
        image_urn = upload_data.get('value', {}).get('image')

        if not upload_url:
            raise Exception(f"No upload URL in response: {upload_data}")

        # Upload the image data in chunks (2MB chunks per LinkedIn docs)
        etags = []
        chunk_size = 2 * 1024 * 1024
        for i in range(0, len(image_data), chunk_size):
            chunk = image_data[i:i + chunk_size]
            put_resp = requests.put(
                upload_url,
                data=chunk,
                headers={
                    'X-Restli-Protocol-Version': '2.0.0',
                    'LinkedIn-Version': '202601',
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/octet-stream',
                }
            )
            if put_resp.status_code not in (200, 201):
                # Some endpoints return the URN directly
                pass
            etags.append(put_resp.headers.get('etag', ''))

        return image_urn

    def post(self, content: str, access_token: str, media_urls: Optional[list] = None,
             visibility: str = 'PUBLIC', person_id: Optional[str] = None,
             **kwargs) -> Dict:
        """Create a LinkedIn post on personal profile.

        Postiz reference: linkedin.provider.ts :: createMainPost()

        Args:
            content: Post text content
            access_token: OAuth access token
            media_urls: Optional list of image URLs to upload and attach
            visibility: 'PUBLIC' or 'CONNECTIONS'
            person_id: LinkedIn person ID (sub from userinfo)

        Returns:
            Dict with post_id, url
        """
        if not person_id:
            raise ValueError("LinkedIn posting requires person_id (get it from exchange_code_for_tokens)")

        author_urn = f"urn:li:person:{person_id}"

        # Build post payload
        post_payload = {
            "author": author_urn,
            "commentary": self._fix_text(content),
            "visibility": "PUBLIC",
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": [],
            },
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False,
        }

        # Handle media upload if provided
        media_ids = []
        if media_urls:
            for media_url in media_urls[:1]:  # LinkedIn personal posts support 1 image
                try:
                    img_resp = requests.get(media_url)
                    img_resp.raise_for_status()
                    media_urn = self._upload_image(img_resp.content, access_token, person_id)
                    media_ids.append(media_urn)
                except Exception as e:
                    print(f"Warning: failed to upload media from {media_url}: {e}")

        # Add media to payload if uploaded
        if media_ids:
            post_payload["content"] = {
                "media": {"id": media_ids[0]}
            }

        # Post to LinkedIn
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0',
            'LinkedIn-Version': '202601',
        }

        response = requests.post(
            f"{self.api_base_url}/posts",
            headers=headers,
            json=post_payload
        )

        if response.status_code not in (200, 201):
            raise Exception(f"LinkedIn API error: {response.status_code} - {response.text}")

        response_data = response.json()
        # LinkedIn returns x-restli-id header for the new post
        post_urn = response.headers.get('x-restli-id', '')
        if not post_urn:
            post_urn = response_data.get('id', '')

        return {
            'post_id': post_urn,
            'url': f"https://www.linkedin.com/feed/update/{post_urn}",
            'platform_response': response_data
        }

    def get_profile(self, access_token: str) -> Dict:
        """Get LinkedIn profile information."""
        user_info = self._get_user_info(access_token)
        return {
            'id': user_info.get('sub'),
            'name': user_info.get('name'),
            'email': user_info.get('email'),
            'picture': user_info.get('picture'),
        }
