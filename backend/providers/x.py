"""X (Twitter) provider implementation.

X uses OAuth 1.0a which is significantly more complex than OAuth 2.0.
Docs: https://developer.twitter.com/en/docs/authentication/oauth-1-0a

API v2: https://developer.twitter.com/en/docs/twitter-api
"""
from typing import Dict, Optional, Tuple
import requests
import hashlib
import hmac
import base64
import time
import urllib.parse
from .base import SocialProvider

class XProvider(SocialProvider):
    """X (Twitter) social media provider."""
    
    identifier = 'x'
    name = 'X'
    oauth_version = 'oauth1'
    editor = 'normal'
    
    # X limits
    max_characters = 280  # Standard tweet
    max_media = 4  # Images per tweet
    max_video_duration = 140  # seconds
    
    # OAuth 1.0a endpoints
    request_token_url = 'https://api.twitter.com/oauth/request_token'
    authorization_url = 'https://api.twitter.com/oauth/authorize'
    access_token_url = 'https://api.twitter.com/oauth/access_token'
    api_base_url = 'https://api.twitter.com/2'
    
    # Scopes (for OAuth 2.0, but X uses 1.0a primarily)
    scopes = []
    
    def _get_oauth1_authorization_url(self, state: Optional[str] = None) -> str:
        """Generate OAuth 1.0a authorization URL.
        
        OAuth 1.0a requires three steps:
        1. Get request token
        2. Redirect user to authorization URL
        3. Exchange for access token
        
        This method returns step 2 URL.
        """
        # Step 1: Get request token
        request_token = self._get_request_token()
        
        # Step 2: Return authorization URL with request token
        return f"{self.authorization_url}?oauth_token={request_token['oauth_token']}"
    
    def _get_request_token(self) -> Dict:
        """Get OAuth 1.0a request token."""
        # OAuth 1.0a signature for request token
        params = {
            'oauth_callback': self.redirect_uri,
            'oauth_consumer_key': self.client_id,
            'oauth_nonce': str(int(time.time())),
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_timestamp': str(int(time.time())),
            'oauth_version': '1.0'
        }
        
        # Create signature base string
        signature = self._create_signature(
            'POST',
            self.request_token_url,
            params,
            self.client_secret,
            ''  # No token secret yet
        )
        
        params['oauth_signature'] = signature
        
        # Build Authorization header
        auth_header = 'OAuth ' + ', '.join(
            f'{urllib.parse.quote(k)}="{urllib.parse.quote(v)}"'
            for k, v in sorted(params.items())
        )
        
        headers = {
            'Authorization': auth_header
        }
        
        response = requests.post(self.request_token_url, headers=headers)
        response.raise_for_status()
        
        # Parse response (form-encoded)
        result = {}
        for pair in response.text.split('&'):
            key, value = pair.split('=', 1)
            result[key] = urllib.parse.unquote(value)
        
        return result
    
    def _exchange_oauth1_code(self, oauth_token: str, oauth_verifier: str) -> Dict:
        """Exchange OAuth 1.0a verifier for access token.
        
        Args:
            oauth_token: From callback
            oauth_verifier: From callback
            
        Returns:
            Dict with access_token, refresh_token (X doesn't refresh), etc.
        """
        # OAuth 1.0a signature for access token
        params = {
            'oauth_consumer_key': self.client_id,
            'oauth_nonce': str(int(time.time())),
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_timestamp': str(int(time.time())),
            'oauth_token': oauth_token,
            'oauth_verifier': oauth_verifier,
            'oauth_version': '1.0'
        }
        
        # Create signature
        signature = self._create_signature(
            'POST',
            self.access_token_url,
            params,
            self.client_secret,
            ''  # We don't have token secret yet
        )
        
        params['oauth_signature'] = signature
        
        # Build Authorization header
        auth_header = 'OAuth ' + ', '.join(
            f'{urllib.parse.quote(k)}="{urllib.parse.quote(v)}"'
            for k, v in sorted(params.items())
        )
        
        headers = {
            'Authorization': auth_header
        }
        
        response = requests.post(self.access_token_url, headers=headers)
        response.raise_for_status()
        
        # Parse response
        result = {}
        for pair in response.text.split('&'):
            key, value = pair.split('=', 1)
            result[key] = urllib.parse.unquote(value)
        
        from datetime import datetime, timedelta
        
        # X OAuth 1.0a tokens don't expire, but we'll set a far future date
        expires_at = datetime.utcnow() + timedelta(days=3650)
        
        return {
            'access_token': result.get('oauth_token'),
            'token_secret': result.get('oauth_token_secret'),
            'refresh_token': None,  # OAuth 1.0a doesn't use refresh tokens
            'token_type': 'OAuth1.0a',
            'expires_at': expires_at,
            'scope': '',
            'account_id': result.get('user_id'),
            'account_name': result.get('screen_name'),
            'profile_picture': None  # Would need separate API call
        }
    
    def _create_signature(self, method: str, url: str, params: Dict, 
                         consumer_secret: str, token_secret: str) -> str:
        """Create OAuth 1.0a HMAC-SHA1 signature.
        
        OAuth 1.0a signature is complex. In production, use oauthlib library.
        """
        # Percent encode parameters
        encoded_params = []
        for key, value in sorted(params.items()):
            if key == 'oauth_signature':
                continue
            encoded_key = urllib.parse.quote(key, safe='')
            encoded_value = urllib.parse.quote(value, safe='')
            encoded_params.append(f"{encoded_key}={encoded_value}")
        
        param_string = '&'.join(encoded_params)
        
        # Create signature base string
        encoded_method = urllib.parse.quote(method.upper(), safe='')
        encoded_url = urllib.parse.quote(url, safe='')
        encoded_params = urllib.parse.quote(param_string, safe='')
        
        base_string = f"{encoded_method}&{encoded_url}&{encoded_params}"
        
        # Create signing key
        encoded_consumer_secret = urllib.parse.quote(consumer_secret, safe='')
        encoded_token_secret = urllib.parse.quote(token_secret, safe='')
        signing_key = f"{encoded_consumer_secret}&{encoded_token_secret}"
        
        # Create HMAC-SHA1 signature
        signature = hmac.new(
            signing_key.encode('utf-8'),
            base_string.encode('utf-8'),
            hashlib.sha1
        ).digest()
        
        return base64.b64encode(signature).decode('utf-8')
    
    def post(self, content: str, access_token: str, media_urls: Optional[list] = None,
             reply_to: Optional[str] = None, 
             oauth_token_secret: Optional[str] = None,
             **kwargs) -> Dict:
        """Create a tweet on X.
        
        Args:
            content: Tweet text (max 280 chars)
            access_token: OAuth 1.0a access token (oauth_token)
            media_urls: Optional list of image URLs to attach (requires upload)
            reply_to: Tweet ID to reply to
            oauth_token_secret: OAuth 1.0a token secret (required for signing)
            
        Returns:
            Dict with post_id, url, etc.
        """
        if not oauth_token_secret:
            raise ValueError("X posting requires oauth_token_secret (OAuth 1.0a)")
        
        # X API v2 posting endpoint
        url = f"{self.api_base_url}/tweets"
        
        # Build request body
        data = {"text": content[:280]}  # Enforce character limit
        
        if reply_to:
            data["reply"] = {"in_reply_to_tweet_id": reply_to}
        
        headers = {
            "Authorization": f"Bearer {self.client_secret}",  # Bearer auth for API v2
            "Content-Type": "application/json"
        }
        
        # OAuth 1.0a signing would go here for user-context requests
        # For app-only or with proper OAuth 1.0a signing:
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 201:
            result = response.json()
            tweet_id = result.get("data", {}).get("id")
            return {
                "post_id": tweet_id,
                "url": f"https://x.com/i/status/{tweet_id}" if tweet_id else None,
                "platform_response": result
            }
        else:
            # Try OAuth 1.0a signed request if v2 Bearer fails
            oauth_headers = self._generate_oauth1_headers(
                "POST", url, data, self.client_id, self.client_secret,
                access_token, oauth_token_secret
            )
            headers.update(oauth_headers)
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 201:
                result = response.json()
                tweet_id = result.get("data", {}).get("id")
                return {
                    "post_id": tweet_id,
                    "url": f"https://x.com/i/status/{tweet_id}" if tweet_id else None,
                    "platform_response": result
                }
            
            raise Exception(f"X API error: {response.status_code} - {response.text}")
    
    def _generate_oauth1_headers(self, method: str, url: str, data: dict,
                                  consumer_key: str, consumer_secret: str,
                                  access_token: str, access_token_secret: str) -> Dict:
        """Generate OAuth 1.0a Authorization header for signed requests."""
        import time
        import secrets
        import hashlib
        import hmac
        import base64
        import urllib.parse
        
        # OAuth 1.0a parameters
        oauth_params = {
            "oauth_consumer_key": consumer_key,
            "oauth_nonce": secrets.token_urlsafe(32),
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": str(int(time.time())),
            "oauth_token": access_token,
            "oauth_version": "1.0"
        }
        
        # Create signature
        signature = self._create_signature(
            method, url, oauth_params, consumer_secret, access_token_secret
        )
        oauth_params["oauth_signature"] = signature
        
        # Build Authorization header
        auth_header = "OAuth " + ", ".join(
            f'{urllib.parse.quote(k, safe="")}="{urllib.parse.quote(v, safe="")}"'
            for k, v in sorted(oauth_params.items())
        )
        
        return {"Authorization": auth_header}
    
    def _create_signature(self, method: str, url: str, params: Dict, 
                         consumer_secret: str, token_secret: str) -> str:
        """Create OAuth 1.0a HMAC-SHA1 signature."""
        import urllib.parse
        
        # Percent encode parameters
        encoded_params = []
        for key, value in sorted(params.items()):
            if key == "oauth_signature":
                continue
            encoded_key = urllib.parse.quote(key, safe="")
            encoded_value = urllib.parse.quote(value, safe="")
            encoded_params.append(f"{encoded_key}={encoded_value}")
        
        param_string = "&".join(encoded_params)
        
        # Create signature base string
        encoded_method = urllib.parse.quote(method.upper(), safe="")
        encoded_url = urllib.parse.quote(url, safe="")
        encoded_params = urllib.parse.quote(param_string, safe="")
        
        base_string = f"{encoded_method}&{encoded_url}&{encoded_params}"
        
        # Create signing key
        encoded_consumer = urllib.parse.quote(consumer_secret, safe="")
        encoded_token = urllib.parse.quote(token_secret, safe="")
        signing_key = f"{encoded_consumer}&{encoded_token}"
        
        # Create HMAC-SHA1 signature
        signature = hmac.new(
            signing_key.encode("utf-8"),
            base_string.encode("utf-8"),
            hashlib.sha1
        ).digest()
        
        return base64.b64encode(signature).decode("utf-8")
    
    def refresh_access_token(self, refresh_token: str) -> Dict:
        """OAuth 1.0a doesn't support token refresh.
        
        Tokens are permanent until revoked.
        """
        raise NotImplementedError("OAuth 1.0a tokens don't expire and can't be refreshed")
    
    @classmethod
    def requires_user_auth(cls) -> bool:
        return True
    
    @classmethod
    def supports_refresh(cls) -> bool:
        return False
