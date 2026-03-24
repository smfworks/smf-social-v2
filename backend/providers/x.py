"""X (Twitter) provider implementation using tweepy.

OAuth 1.0a with tweepy — cleaner than hand-rolled signing.
Token stored as: access_token:access_token_secret (Postiz pattern)

Reference: Postiz x.provider.ts
"""
from typing import Dict, Optional
import tweepy
from .base import SocialProvider


class XProvider(SocialProvider):
    """X (Twitter) provider using tweepy."""

    identifier = 'x'
    name = 'X'
    oauth_version = 'oauth1a'
    editor = 'normal'

    # X limits
    max_characters = 280  # Basic tier
    max_media = 4  # Images

    # OAuth endpoints
    authorization_url = 'https://api.twitter.com/oauth/authenticate'
    api_base_url = 'https://api.twitter.com/2'

    def __init__(self, credentials: Dict):
        super().__init__(credentials)
        self.client_id = credentials.get('client_id')
        self.client_secret = credentials.get('client_secret')
        self.redirect_uri = credentials.get('redirect_uri')

    def _split_token(self, token: str) -> tuple:
        """Split stored token into access_token and access_token_secret.

        Token is stored as: access_token:access_token_secret
        (Postiz pattern from x.provider.ts)
        """
        parts = token.split(':')
        if len(parts) == 2:
            return parts[0], parts[1]
        # Fallback for tokens stored old way
        return token, None

    def exchange_code_for_tokens(self, code: str) -> Dict:
        """Exchange OAuth 1.0a verifier code for access tokens.

        Note: X OAuth 1.0a uses oauth_verifier, not authorization_code.
        This method is for the callback after user authorizes.
        """
        raise NotImplementedError(
            "X OAuth 1.0a uses a different flow. "
            "Use generate_auth_url() to get the authorization URL, "
            "then authenticate() with the verifier code."
        )

    def generate_auth_url(self) -> Dict:
        """Generate X OAuth 1.0a authorization URL.

        Returns dict with:
            url: The authorization URL to visit
            code_verifier: oauth_token:oauth_token_secret (store for authenticate)
            state: OAuth state parameter
        """
        oauth_handler = tweepy.OAuthHandler(
            self.client_id,
            self.client_secret,
            self.redirect_uri
        )

        # Get authorization URL
        try:
            redirect_url = oauth_handler.get_authorization_url()
        except tweepy.TweepyException as e:
            raise Exception(f"Failed to generate auth URL: {e}")

        # Store the request token for later token exchange
        # tweepy stores oauth_token and oauth_token_secret internally
        return {
            'url': redirect_url,
            'code_verifier': f"{oauth_handler.request_token['oauth_token']}:{oauth_handler.request_token['oauth_token_secret']}",
            'state': oauth_handler.request_token.get('oauth_token', '')
        }

    def authenticate(self, code_verifier: str) -> Dict:
        """Exchange authorization code for access tokens.

        Args:
            code_verifier: The oauth_verifier from the callback URL,
                         OR the full oauth_token:oauth_token_secret string

        For X OAuth 1.0a, we use the request token to get access tokens.
        """
        oauth_token, oauth_token_secret = code_verifier.split(':')

        oauth_handler = tweepy.OAuthHandler(
            self.client_id,
            self.client_secret,
            self.redirect_uri
        )
        oauth_handler.request_token = {
            'oauth_token': oauth_token,
            'oauth_token_secret': oauth_token_secret
        }

        # Get the verifier from callback
        # In a real flow, the callback URL contains oauth_verifier
        # Here we treat code_verifier as the oauth_verifier directly
        try:
            # Exchange request token for access token
            # X OAuth 1.0a uses get_access_token with the verifier
            access_token, access_token_secret = oauth_handler.get_access_token(code_verifier)
        except tweepy.TweepyException as e:
            raise Exception(f"Failed to get access token: {e}")

        # Build client with access token
        client = tweepy.Client(
            consumer_key=self.client_id,
            consumer_secret=self.client_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )

        # Get user info
        try:
            user = client.get_user(username=access_token)
            me = client.get_me()
            user_data = me.data or {}
            username = user.data.get('username', '') if user.data else ''
        except Exception:
            username = 'unknown'

        return {
            'access_token': f"{access_token}:{access_token_secret}",  # Postiz pattern
            'refresh_token': None,  # OAuth 1.0a doesn't use refresh tokens
            'token_type': 'OAuth1.0a',
            'expires_at': None,  # OAuth 1.0a tokens don't expire
            'account_id': str(user_data.get('id', '')),
            'account_name': user_data.get('name', ''),
            'username': username,
            'profile_picture': user_data.get('profile_image_url', '')
        }

    def refresh_token(self, refresh_token: str) -> Dict:
        """OAuth 1.0a tokens don't refresh — they're permanent."""
        return {
            'access_token': refresh_token,  # Already the access_token:secret combo
            'refresh_token': None,
            'expires_at': None
        }

    def post(self, content: str, access_token: str, media_urls: Optional[list] = None,
             reply_to: Optional[str] = None, **kwargs) -> Dict:
        """Post a tweet to X.

        Args:
            content: Tweet text (max 280 chars for basic tier)
            access_token: Stored as "access_token:access_token_secret"
            media_urls: List of image URLs to upload and attach
            reply_to: Tweet ID to reply to

        Returns:
            Dict with post_id, url
        """
        access_token_val, access_token_secret = self._split_token(access_token)

        # Build tweepy client
        client = tweepy.Client(
            consumer_key=self.client_id,
            consumer_secret=self.client_secret,
            access_token=access_token_val,
            access_token_secret=access_token_secret
        )

        # Upload media if provided
        media_ids = []
        if media_urls:
            # Media upload requires OAuth 1.0a auth
            auth = tweepy.OAuthHandler(
                self.client_id,
                self.client_secret
            )
            auth.set_access_token(access_token_val, access_token_secret)
            api = tweepy.API(auth)

            for media_url in media_urls[:self.max_media]:
                try:
                    # Download image
                    import requests
                    img_resp = requests.get(media_url)
                    img_resp.raise_for_status()

                    # Upload to X
                    media = api.media_upload(
                        filename=media_url.split('/')[-1],
                        file=img_resp.content
                    )
                    media_ids.append(media.media_id_string)
                except Exception as e:
                    print(f"Warning: failed to upload media from {media_url}: {e}")

        # Build tweet params
        tweet_params = {'text': content[:280]}

        if media_ids:
            tweet_params['media'] = {'media_ids': media_ids}

        if reply_to:
            tweet_params['reply'] = {'in_reply_to_tweet_id': reply_to}

        # Post tweet
        response = client.create_tweet(**tweet_params)

        if response.data:
            tweet_id = response.data['id']
            return {
                'post_id': tweet_id,
                'url': f"https://x.com/i/status/{tweet_id}",
                'platform_response': response.data
            }
        else:
            raise Exception(f"X post failed: {response}")

    def get_profile(self, access_token: str) -> Dict:
        """Get X profile information."""
        access_token_val, access_token_secret = self._split_token(access_token)

        client = tweepy.Client(
            consumer_key=self.client_id,
            consumer_secret=self.client_secret,
            access_token=access_token_val,
            access_token_secret=access_token_secret
        )

        me = client.get_me()
        if me.data:
            return {
                'id': me.data.get('id'),
                'name': me.data.get('name'),
                'username': me.data.get('username'),
                'profile_picture': me.data.get('profile_image_url')
            }
        return {}
