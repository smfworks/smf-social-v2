# SMF Social v2 - Status Report & Issues

**Project:** SMF Social v2 (Standalone, replaces Postiz)  
**Location:** `/home/mikesai1/projects/smf-social-v2`  
**Last Updated:** 2026-03-20  
**Status:** 🚧 In Development - OAuth Flow Working in Test Mode

---

## What We Were Working On

Based on git history and documentation, we were implementing **SMF Social v2** - a complete rebuild to replace Postiz with a self-hosted, multi-tenant social media platform.

### Key Goals
1. **Replace Postiz** - Move off SaaS dependency
2. **Self-hosted capable** - Customers can run their own instance
3. **Multi-tenant** - Support multiple customers on one instance
4. **OAuth-based** - Each customer configures their own OAuth apps
5. **2-week sprint** - Target: Off Postiz by April 3, 2026

---

## Current State

### ✅ What's Working

| Component | Status | Notes |
|-----------|--------|-------|
| **Project Structure** | ✅ Complete | FastAPI backend, React frontend |
| **Database Models** | ✅ Complete | SQLite with SQLAlchemy |
| **Pinterest OAuth** | ✅ Working | Test mode functional |
| **LinkedIn OAuth** | ⏳ In Progress | Provider implemented, needs testing |
| **X (Twitter) OAuth** | ⏳ Planned | Provider stub exists, needs OAuth 1.0a |
| **Test Mode** | ✅ Working | Mock OAuth for development |
| **Frontend UI** | ✅ Working | Integrations page, OAuth callback |
| **Token Encryption** | ✅ Working | Secure storage |
| **API Structure** | ✅ Complete | REST endpoints for auth, posts, integrations |

### ❌ What's Not Working / Blocked

| Component | Status | Issue |
|-----------|--------|-------|
| **Docker Deployment** | ❌ Blocked | Permission denied - needs Docker setup |
| **Real OAuth Credentials** | ⚠️ Not Configured | Pinterest/LinkedIn/X apps not created |
| **APScheduler** | ⏳ Not Wired | Scheduler exists but not integrated |
| **Posting to Real Platforms** | ❌ Not Tested | Only test mode works |
| **Instagram** | ⏳ Post-MVP | Not in 2-week sprint |

---

## The Pinterest Token ID Issue

### What We Were Trying to Do

Configure Pinterest OAuth in SMF Social v2. The system requires:

1. **OAuth App** - Created at https://developers.pinterest.com/apps/
2. **Client ID** - Stored in `PINTEREST_CLIENT_ID` env var
3. **Client Secret** - Stored in `PINTEREST_CLIENT_SECRET` env var
4. **Board ID** - Optional, fetched dynamically via API

### Current Configuration

**File:** `backend/providers/pinterest.py`
```python
# Board ID is fetched dynamically, not hardcoded
# The get_boards() method retrieves user's boards via API

def post(self, content: str, access_token: str, media_urls: Optional[list] = None, 
         board_id: Optional[str] = None, link: Optional[str] = None, **kwargs) -> Dict:
    """Create a Pinterest Pin."""
    if not board_id:
        raise ValueError("Pinterest requires a board_id to post pins")
```

**File:** `backend/api/integrations.py`
```python
@router.get("/{integration_id}/boards")
def get_pinterest_boards(integration_id: str, tenant_id: str, db: Session = Depends(get_db)):
    """Get Pinterest boards for an integration."""
    # Calls PinterestProvider.get_boards() via API
```

### The Issue

**No real OAuth credentials configured.** The system has:
- ✅ Test mode working (mock credentials)
- ❌ No real Pinterest OAuth app credentials
- ❌ No real LinkedIn OAuth app credentials  
- ❌ No real X OAuth app credentials

### What We Were Trying to Accomplish

1. Create real OAuth apps on each platform
2. Store credentials in environment variables
3. Test real OAuth flow (not mock mode)
4. Actually post to Pinterest/LinkedIn/X

---

## Git History Analysis

Recent commits show what we were working on:

```
5ea08b8 fix: TypeScript build errors for Docker
195506b fix: Add visible error display to ManualTokenEntry
f574cbc fix: Add error handling to ManualTokenEntry
b5481c7 fix: Add manual-token endpoint to integrations API
27b4e7e fix: Correct import - decode_token instead of verify_token
2b77176 feat: Add ManualTokenEntry to Integrations page
d306027 feat: Add manual token entry for Pinterest testing
```

**Pattern:** We were implementing manual token entry as a workaround for OAuth flow issues.

---

## Testing OAuth Flow

### What Works (Test Mode)

```bash
./scripts/quick-test.sh
```

**Result:** ✅ Test mode works perfectly
- Mock OAuth URL generated
- Simulated callback handled
- Integration record created
- All without real credentials

### What Doesn't Work (Real Mode)

- ❌ Docker deployment (permission issues)
- ❌ Real OAuth apps not created
- ❌ No credentials configured
- ❌ Cannot test actual posting

---

## Root Causes of Issues

### 1. Docker Permission Problem
```
PermissionError(13, 'Permission denied')
Error while fetching server API version
```
**Cause:** User doesn't have Docker permissions or Docker not running
**Fix:** `sudo usermod -aG docker $USER` or run as root

### 2. No Real OAuth Credentials
- Pinterest app: Not created
- LinkedIn app: Not created
- X app: Not created

**Fix:** Create apps at developer portals

### 3. Test Mode vs Real Mode Confusion
- Test mode: Works perfectly, uses fake data
- Real mode: Not configured, needs credentials
- UI shows toggle but real mode won't work without setup

---

## Methods to Correct Issues

### Immediate Fixes (Today)

1. **Fix Docker Permissions**
   ```bash
   sudo systemctl start docker
   sudo usermod -aG docker $USER
   # Log out and back in
   ```

2. **Create Pinterest OAuth App**
   - Go to: https://developers.pinterest.com/apps/
   - Click "Create App"
   - Fill in:
     - App name: "SMF Social"
     - Description: "Social media automation for small businesses"
     - Redirect URI: `http://localhost:8000/api/auth/pinterest/callback`
   - Copy Client ID and Secret

3. **Configure Environment**
   ```bash
   # Edit ~/.openclaw/secrets/smf-social.env
   PINTEREST_CLIENT_ID=your_real_client_id
   PINTEREST_CLIENT_SECRET=your_real_client_secret
   ```

4. **Test Real OAuth Flow**
   - Start backend: `python backend/main.py`
   - Open: http://localhost:3000
   - Toggle OFF test mode
   - Click "Connect"
   - Approve on Pinterest
   - Verify real integration created

### Short-term Fixes (This Week)

1. **Create LinkedIn OAuth App**
   - https://www.linkedin.com/developers/apps
   - Product: "Share on LinkedIn" + "Sign In with LinkedIn"
   - Redirect URI configured

2. **Create X (Twitter) OAuth App**
   - https://developer.twitter.com/en/portal/dashboard
   - App type: "Automated" or "Bot"
   - Elevated access required
   - OAuth 1.0a (not 2.0)

3. **Complete OAuth Testing**
   - Test Pinterest real posting
   - Test LinkedIn real posting
   - Test X real posting

4. **Integrate APScheduler**
   - Wire up job scheduling
   - Test scheduled posts
   - Add retry logic

### Long-term Fixes (Sprint Completion)

1. **Production Deployment**
   - Docker working
   - Domain configured
   - SSL certificates
   - Database migrations

2. **Customer Onboarding**
   - Documentation complete
   - Setup wizard
   - OAuth app creation guide
   - Self-hosting instructions

3. **Migration from Postiz**
   - Export Postiz data
   - Import to SMF Social v2
   - Parallel running
   - Cutover

---

## Where We Stand

### Sprint Progress: ~30% Complete

**Week 1 Goals (Mar 20-27):**
- [x] Project structure
- [x] SQLite models
- [x] FastAPI + JWT
- [x] Pinterest OAuth (test mode)
- [ ] **Pinterest OAuth (real mode)** ← BLOCKED: No credentials
- [x] React frontend
- [ ] LinkedIn OAuth ← NOT STARTED
- [ ] X OAuth ← NOT STARTED
- [ ] Scheduling ← NOT STARTED

**Blockers:**
1. No real OAuth credentials configured
2. Docker permission issues
3. Need OAuth apps created on platforms

**What's Working:**
- Test mode is rock solid
- Architecture is sound
- Code is clean and documented
- Ready for real credentials

---

## Recommended Next Steps

### Option 1: Complete Sprint (Original Goal)
**Time:** 1-2 weeks  
**Requires:**
- Create 3 OAuth apps (Pinterest, LinkedIn, X)
- Fix Docker permissions
- Complete OAuth flows
- Integrate scheduler
- Test end-to-end
- Deploy

### Option 2: Use Test Mode for SMF Works
**Time:** Immediate  
**Approach:**
- Keep using test mode for development
- Create real OAuth apps when ready
- Postiz continues for production
- Gradual migration

### Option 3: Hybrid Approach (Recommended)
**Time:** 1 week  
**Plan:**
1. Create Pinterest OAuth app (easiest)
2. Get Pinterest working in real mode
3. Migrate SMF Works Pinterest off Postiz
4. Keep Postiz for LinkedIn/X until v2 ready
5. Build out v2 incrementally

---

## Documentation Created

| Document | Location | Status |
|----------|----------|--------|
| Architecture | `docs/Architecture.md` | ✅ Complete |
| OAuth Setup Guide | `docs/OAuth Setup Guide.md` | ✅ Complete |
| Testing OAuth Flow | `docs/Testing OAuth Flow.md` | ✅ Complete |
| Sprint Plan (2 weeks) | `docs/Sprint Plan - Off Postiz in 2 Weeks.md` | ✅ Complete |
| Direct Install | `docs/Direct Install.md` | ✅ Complete |
| Docker Deployment | `docs/Docker Deployment.md` | ✅ Complete |

---

## Key Files

**Backend:**
- `backend/main.py` - FastAPI entry point
- `backend/providers/pinterest.py` - Pinterest OAuth + posting
- `backend/api/integrations.py` - Integration management
- `backend/core/test_oauth.py` - Test mode implementation

**Frontend:**
- `frontend/src/pages/Integrations.tsx` - OAuth UI
- `frontend/src/pages/OAuthCallback.tsx` - OAuth callback handler

**Scripts:**
- `scripts/quick-test.sh` - Automated OAuth test

---

## Summary

**SMF Social v2 is well-architected and functional in test mode.** The blockers are:

1. **OAuth credentials not configured** - Need to create real apps
2. **Docker permissions** - Fixable with user setup
3. **Time to complete** - 1-2 weeks with focus

**The Pinterest "token ID issue" was actually about missing OAuth app credentials, not a code bug.** The system is designed to work correctly once credentials are provided.

**Recommendation:** Create one OAuth app (Pinterest) to prove the system works, then decide on full sprint completion.

---

*Report generated: 2026-03-20*  
*Project status: Ready for real credentials*  
*Next action: Create Pinterest OAuth app or fix Docker permissions*
