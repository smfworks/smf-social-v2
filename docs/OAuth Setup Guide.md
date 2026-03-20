# OAuth App Setup Guide

**For:** SMF Social v2 Testing  
**Last Updated:** 2026-03-20

---

## Overview

Each customer must create their own OAuth apps on social platforms. This guide walks through creating test apps for development.

---

## Pinterest (Easiest - Start Here)

### 1. Create Pinterest Business Account
- Go to https://business.pinterest.com/
- Sign up with your email

### 2. Create OAuth App
1. Visit https://developers.pinterest.com/
2. Click "Create App"
3. Fill in details:
   - **App Name:** "SMF Social Test" (or your preference)
   - **Description:** "Social media automation testing"
   - **Website:** `http://localhost`
4. Save Client ID and Secret

### 3. Configure OAuth
- **Redirect URI:** `http://localhost/api/auth/pinterest/callback`
- **Scopes:** `boards:read`, `boards:write`, `pins:read`, `pins:write`, `user_accounts:read`

### 4. Test Credentials File
Create `~/.openclaw/secrets/pinterest-test.env`:
```bash
# Pinterest OAuth Test Credentials
PINTEREST_CLIENT_ID=your_client_id_here
PINTEREST_CLIENT_SECRET=your_client_secret_here
PINTEREST_REDIRECT_URI=http://localhost/api/auth/pinterest/callback
```

---

## LinkedIn

### 1. Create LinkedIn Developer Account
- Go to https://developer.linkedin.com/
- Sign in with LinkedIn account

### 2. Create App
1. Click "Create App"
2. Fill in:
   - **App Name:** "SMF Social Test"
   - **LinkedIn Page:** Create a test page or use personal
   - **Privacy Policy URL:** `http://localhost/privacy`
   - **App Logo:** Upload any image

### 3. Configure OAuth 2.0
- **Authorized Redirect URLs:** `http://localhost/api/auth/linkedin/callback`
- **Scopes:** `openid`, `profile`, `email`, `w_member_social`

### 4. Verify App (Required for posting)
- Submit for review (takes 1-5 days)
- Or use Developer Mode for testing

### 5. Test Credentials
```bash
# LinkedIn OAuth Test Credentials
LINKEDIN_CLIENT_ID=your_client_id_here
LINKEDIN_CLIENT_SECRET=your_client_secret_here
LINKEDIN_REDIRECT_URI=http://localhost/api/auth/linkedin/callback
```

---

## X (Twitter) - Most Complex

### 1. Apply for Developer Account
- Go to https://developer.twitter.com/
- Apply for Basic access (free)
- Wait for approval (usually instant)

### 2. Create Project and App
1. Create a Project
2. Create an App within the project
3. Enable "User authentication settings"

### 3. Configure OAuth 1.0a
- **App permissions:** Read and Write
- **Callback URL:** `http://localhost/api/auth/x/callback`
- **Website URL:** `http://localhost`

### 4. Get Keys
You need TWO sets of keys:
- **API Key and Secret** (for OAuth 1.0a)
- **Access Token and Secret** (for your account)

### 5. Test Credentials
```bash
# X OAuth Test Credentials
X_API_KEY=your_api_key_here
X_API_SECRET=your_api_secret_here
X_ACCESS_TOKEN=your_access_token_here
X_ACCESS_SECRET=your_access_secret_here
X_REDIRECT_URI=http://localhost/api/auth/x/callback
```

---

## Loading Test Credentials into SMF Social v2

### Option 1: Environment Variables
```bash
export POSTIZ_CHANNEL_PINTEREST="your_pinterest_channel_id"
export PINTEREST_CLIENT_ID="your_client_id"
export PINTEREST_CLIENT_SECRET="your_secret"
```

### Option 2: Secrets File
Edit `~/.openclaw/secrets/smf-social.env`:
```bash
# SMF Social v2 - Test Credentials

# Pinterest
PINTEREST_CLIENT_ID=xxx
PINTEREST_CLIENT_SECRET=xxx
PINTEREST_REDIRECT_URI=http://localhost/api/auth/pinterest/callback

# LinkedIn
LINKEDIN_CLIENT_ID=xxx
LINKEDIN_CLIENT_SECRET=xxx
LINKEDIN_REDIRECT_URI=http://localhost/api/auth/linkedin/callback

# X
X_API_KEY=xxx
X_API_SECRET=xxx
X_ACCESS_TOKEN=xxx
X_ACCESS_SECRET=xxx
```

### Option 3: UI Configuration (Future)
In the SMF Social v2 web UI:
- Go to Settings → OAuth Apps
- Paste credentials for each platform
- Save and verify

---

## Testing OAuth Flow

### 1. Start Backend
```bash
cd ~/smf-social-v2/backend
python main.py
```

### 2. Start Frontend
```bash
cd ~/smf-social-v2/frontend
npm run dev
```

### 3. Test Connection
1. Open http://localhost:3000
2. Go to Integrations
3. Click "Connect" next to Pinterest
4. Should redirect to Pinterest authorization
5. After auth, redirect back to SMF Social
6. Status should show "Connected"

---

## Troubleshooting

### "redirect_uri mismatch"
- Check that the redirect URI in your OAuth app EXACTLY matches
- Must include `http://` or `https://`
- Must match the port (e.g., `:3000`)

### "client_id invalid"
- Verify you're using the correct ID (not the secret)
- Check for extra spaces or characters

### "insufficient permissions"
- Verify scopes requested match app settings
- Some platforms require approval for write access

### Callback not received
- Check browser network tab for redirect
- Verify backend is running on correct port
- Check CORS settings in backend

---

## Production vs Test

| Aspect | Test | Production |
|--------|------|------------|
| App Name | "SMF Social Test" | "Your Company Name" |
| Redirect URI | localhost | yourdomain.com |
| Rate Limits | Lower | Higher |
| Approval | Instant or days | May require business verification |
| Branding | Optional | Required |

---

## Platform-Specific Notes

### Pinterest
- **Easiest** to set up
- **Fastest** approval (instant)
- Good starting point for testing

### LinkedIn
- Requires business page
- UGC API requires review
- Can test with Developer Mode

### X
- **Hardest** OAuth 1.0a
- Requires API keys + access tokens
- Rate limits very strict

---

## Quick Test Checklist

- [ ] Pinterest app created
- [ ] Pinterest credentials saved
- [ ] Backend running on :8000
- [ ] Frontend running on :3000
- [ ] CORS configured
- [ ] Clicked "Connect" on Integrations page
- [ ] Successfully authorized on platform
- [ ] Returned to SMF Social showing "Connected"

---

## Next Steps

Once OAuth is working:
1. Test posting (create post → publish)
2. Verify media uploads
3. Test scheduling (APScheduler)
4. Move to production OAuth apps

---

**Questions?** Check backend logs: `docker-compose logs -f backend`
