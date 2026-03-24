# SMF Social v2 - Status Report

**Project:** SMF Social v2 (Standalone, replaces Postiz)  
**Location:** `/home/mikesai1/projects/smf-social-v2`  
**Last Updated:** 2026-03-24  
**Status:** 🚧 **ON HOLD — LinkedIn Auth Blocked**

---

## 🚨 Project Status: ON HOLD

**As of 2026-03-24, SMF Social v2 is on hold due to LinkedIn API access restrictions.**

LinkedIn's Developer Portal now requires a Company Page to create a developer app — even for personal profile posting. This blocks the entire multi-platform social publishing concept since:

1. LinkedIn personal profile posting is the core use case
2. Without LinkedIn, the product doesn't meet the original goal of replacing Postiz
3. Other platforms (X, Instagram, Facebook) have similar partnership/app requirements

**Timeline Impact:** Original target of April 3, 2026 is no longer achievable.

---

## What Changed (2026-03-24)

### LinkedIn Blocker Confirmed

After research and Android phone testing:

1. **LinkedIn Developer Portal requires a Company Page** to create an app — even for `w_member_social` scope (personal profile posting)
2. **Postiz has the same bug** (GitHub issue #1197) — their LinkedIn personal profile flow fails with `NotEnoughScopes` because LinkedIn validates all scopes, not just the ones needed
3. **No workaround exists** — this is a LinkedIn business policy gate, not a technical limitation
4. **Reference:** [Postiz issue #1197](https://github.com/gitroomhq/postiz-app/issues/1197)

### What We Tried

- Android phone testing to create LinkedIn developer app
- Reviewing Postiz source code for their LinkedIn implementation
- Researching alternative auth methods (none found)
- Checking if personal OAuth apps work without a Company Page (they don't)

---

## Current Platform Status

| Platform | Status | Notes |
|----------|--------|-------|
| **X (Twitter)** | ✅ Working | Real OAuth 1.0a, posts published, $0.03/post |
| **LinkedIn** | ❌ Blocked | Requires Company Page for dev app — no workaround |
| **Instagram** | ❌ Blocked | Meta developer app + business account required |
| **Facebook** | ❌ Blocked | Same as Instagram — Meta ecosystem |
| **Pinterest** | ❌ Removed | Application rejected by Pinterest |
| **TikTok** | 🔲 Not started | Most complex, save for later |

---

## What Was Working (Before Hold)

| Component | Status | Notes |
|-----------|--------|-------|
| **X OAuth 1.0a** | ✅ Complete | Consumer Key/Secret + Access Token/Secret obtained |
| **X Posting** | ✅ Verified | Real posts to @smfworks, $0.03/post text |
| **LinkedIn Provider** | ✅ Code Ready | Full implementation with image upload |
| **Pinterest** | ❌ Removed | Application rejected |
| **Test Mode** | ✅ Working | Mock OAuth for development |
| **Frontend UI** | ✅ Working | Integrations page, OAuth callback |
| **Token Encryption** | ✅ Working | Secure storage |

---

## Root Cause

**LinkedIn API Access Policy:**
- LinkedIn requires a Company Page to create developer apps
- Even for personal profile posting with `w_member_social` scope
- This is a LinkedIn business restriction, not a technical limitation
- No code or workaround can bypass this

**Postiz Confirmation:**
- Postiz (the SaaS we're replacing) has the same bug (issue #1197)
- Their personal LinkedIn flow fails for users without Company Pages
- This means NO social publishing tool works for LinkedIn personal profiles without a Company Page

**Industry Context:**
- LinkedIn is the only major platform with this restriction
- Other platforms (X, Meta) have OAuth but require developer partnerships for full API access
- Social media automation tools either:
  - Have LinkedIn partner status (expensive)
  - Work around it with browser automation (against ToS)
  - Only support Company Pages

---

## Decision

**SMF Social v2 is paused until:**
1. LinkedIn changes their developer policy, OR
2. We acquire LinkedIn Marketing Partner status, OR
3. We pivot to a Company Page-only model

**Alternative Consideration:**
The X-only implementation is functional and could be released as "SMF Social v2 — X Edition" as a standalone product. However, this doesn't meet the original goal of replacing Postiz.

---

## Files to Reference

**Working X Implementation:**
- `backend/providers/x.py` — tweepy-based X provider
- `backend/providers/linkedin.py` — LinkedIn provider (code complete, auth blocked)
- `docs/OAuth Setup Guide.md` — X OAuth walkthrough

**Recent Commits:**
- `cd8eefd4` — X + LinkedIn provider rewrites
- `dfc0e26` — SMF SEO+GEO update

---

## Next Steps (When Resuming)

If LinkedIn restrictions lift or we decide to proceed with Company Page requirement:

1. **Create LinkedIn Developer App** (requires Company Page)
   - Product: "Share on LinkedIn" + "Sign In with LinkedIn using OpenID Connect"
   - Scopes: `openid profile w_member_social`
   - Redirect: `http://localhost:8000/api/auth/linkedin/callback`

2. **Complete OAuth Flow**
   - Test personal profile posting
   - Verify image upload works

3. **Meta Developer App** (Instagram/Facebook)
   - Create app at developers.facebook.com
   - Enable Instagram Graph API
   - Test business account posting

4. **Production Deployment**
   - Docker setup
   - Domain + SSL
   - Multi-tenant architecture

---

*Report generated: 2026-03-24*  
*Project status: ON HOLD*  
*Blocker: LinkedIn Developer Portal requires Company Page*  
*Last working platform: X (Twitter)*
