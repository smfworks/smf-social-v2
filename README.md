# SMF Social v2 - Standalone Multi-Tenant Social Media Platform

**Status:** 🚧 **ON HOLD** — LinkedIn Auth Blocked (2026-03-24)  
**Architecture:** Multi-tenant, customer-self-hosted capable  
**Last Updated:** 2026-03-24

---

## 🚨 Project On Hold

**As of 2026-03-24, this project is on hold.**

LinkedIn's Developer Portal requires a Company Page to create a developer app — even for personal profile posting. Since LinkedIn was the core use case for replacing Postiz, the project cannot proceed as designed.

**See [STATUS_REPORT.md](./STATUS_REPORT.md) for full details.**

---

## Overview

SMF Social v2 is a **complete rebuild** of the social media automation platform. Unlike v1 (which leverages Postiz SaaS), v2 is a **standalone solution** where each customer:

- Configures their own OAuth apps on social platforms
- Stores their own tokens (encrypted)
- Has complete data isolation
- Can self-host or use our SaaS

**Migration Strategy:**
- v1 (Postiz-based) continues running for SMF Works
- v2 under development
- Gradual migration of SMF Works to v2
- Future customers onboard directly to v2

---

## Architecture

```
smf-social-v2/
├── backend/           # FastAPI/Python backend
│   ├── api/          # REST endpoints
│   ├── providers/    # Platform-specific implementations
│   ├── scheduler/    # Job queue (APScheduler)
│   ├── models/       # Database models (SQLAlchemy)
│   ├── services/     # Business logic
│   └── core/         # Config, auth, db
├── frontend/         # React + Vite frontend
│   └── src/
├── database/         # Migrations
├── docs/             # Documentation
└── scripts/          # Setup, deployment
```

### Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Backend | FastAPI (Python 3.12) | REST API, async handlers |
| Database | SQLite | Single-tenant data (no separate service needed) |
| Queue | APScheduler | Job scheduling (embedded, free) |
| Frontend | React + Vite | Admin UI |
| Auth | OAuth 2.0 + OAuth 1.0a | Platform connections |
| Container | Docker + Compose | Deployment and isolation |

---

## Customer Deployment Models

### Model A: Self-Hosted (Single-Tenant)
**For:** Enterprise customers who want full control

- Customer deploys Docker Compose on their infrastructure
- Customer creates their own OAuth apps (branded to them)
- Complete data isolation
- SMF Works provides: software, documentation, support

### Model B: SMF SaaS (Multi-Tenant)
**For:** SMBs who want managed service

- SMF Works hosts multi-tenant instance
- Customer authorizes our OAuth apps OR creates their own
- Subdomain per customer: `customer.smf-social.com`
- SMF Works manages: infrastructure, updates, support

---

## Platform Support Roadmap

| Phase | Platforms | Timeline |
|-------|-----------|----------|
| **Phase 1** | Pinterest (easiest), LinkedIn (high value) | 2-3 weeks |
| **Phase 2** | X (hardest OAuth), Instagram | 2-3 weeks |
| **Phase 3** | TikTok, YouTube | 2 weeks |
| **Phase 4** | Facebook, Bluesky, others | Future |

---

## OAuth Strategy

### Customer Creates Own Apps (Recommended)
**Pros:**
- Full branding control
- No rate limit sharing
- Platform compliance

**Cons:**
- Setup friction
- Customer must maintain apps

### SMF Creates Shared Apps
**Pros:**
- One-click setup
- Easier onboarding

**Cons:**
- Rate limit shared across customers
- Platform policy risks
- Dependency on SMF

**Decision:** Support both, recommend customer apps

---

## Database Schema (Multi-Tenant)

```sql
-- Tenants table
tenants:
  id, name, slug, created_at, settings

-- OAuth credentials (per tenant, per platform)
oauth_apps:
  id, tenant_id, platform, client_id, client_secret, 
  redirect_uri, scopes, is_active

-- User connections (tokens)
integrations:
  id, tenant_id, platform, account_name, account_id,
  access_token (encrypted), refresh_token (encrypted),
  expires_at, profile_picture, settings

-- Posts
posts:
  id, tenant_id, integration_id, content, media_urls,
  scheduled_for, published_at, status, platform_response

-- Media uploads
media:
  id, tenant_id, file_path, file_url, mime_type, 
  platform_id, upload_status
```

---

## API Structure

### Authentication
```
POST /auth/login              # JWT token
POST /auth/refresh            # Refresh JWT
```

### Integrations (OAuth)
```
GET   /integrations                    # List connected accounts
POST  /integrations/{platform}/connect  # Start OAuth flow
GET   /auth/{platform}/callback        # OAuth callback
DELETE /integrations/{id}             # Disconnect
```

### Posts
```
POST   /posts                 # Create scheduled post
GET    /posts                 # List posts
GET    /posts/{id}            # Get post
PATCH  /posts/{id}            # Update post
DELETE /posts/{id}            # Delete scheduled post
POST   /posts/{id}/publish    # Publish immediately
```

### Scheduler
```
GET    /scheduler/status      # Queue status
POST   /scheduler/pause       # Pause processing
POST   /scheduler/resume      # Resume processing
```

---

## Development Status

| Component | Status | Notes |
|-----------|--------|-------|
| Project structure | ✅ Done | Initial setup complete |
| Database models | 🚧 In progress | SQLAlchemy schemas |
| OAuth flows | 🚧 In progress | Pinterest first |
| Posting API | ⏳ Planned | After OAuth |
| Scheduler | ⏳ Planned | APScheduler |
| Frontend | ⏳ Planned | React admin UI |
| Documentation | 🚧 In progress | This file, setup guides |

---

## Quick Start (Docker - Recommended)

Docker is the **recommended** way to run SMF Social v2. It handles all dependencies automatically and works identically on all platforms.

### Requirements
- Docker 20.10+
- Docker Compose 2.0+
- Git

### 1. Clone Repository

```bash
git clone https://github.com/smfworks/smf-social-v2.git
cd smf-social-v2
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings (optional for testing)
```

### 3. Start with Docker Compose

```bash
docker-compose up -d --build
```

This starts 3 containers:
- **backend** (port 8000) - FastAPI + SQLite
- **frontend** (port 80) - React + nginx
- **nginx** - Reverse proxy

### 4. Access the App

Open your browser: **http://localhost**

### 5. Run Tests

```bash
# Automated OAuth test
./scripts/quick-test.sh

# Check logs
docker-compose logs -f backend
```

### 6. Stop

```bash
docker-compose down
```

---

## Alternative: Direct Install (Not Recommended)

Only use direct install if Docker is not available. Requires:
- Python 3.11+
- Node.js 18+
- SQLite

See [Direct Install Guide](docs/Direct Install.md) for details.

**Note:** Direct install has platform-specific issues (e.g., PEP 668 on Ubuntu 24.04). Docker avoids these problems.

---

## Migration from v1 (Postiz)

When ready to migrate SMF Works:

1. Export Postiz data (scheduled posts, media)
2. Set up v2 instance
3. Create OAuth apps for SMF Works accounts
4. Reconnect platforms in v2
5. Migrate scheduled posts
6. Run parallel for 1-2 weeks
7. Switch DNS/point scripts to v2
8. Sunset Postiz integration

See [[Migration Guide]] (TODO)

---

## Documentation

| Document | Status |
|----------|--------|
| [[Architecture]] | 🚧 Draft |
| [[Database Schema]] | 🚧 Draft |
| [[API Reference]] | ⏳ Planned |
| [[OAuth Setup Guide]] | 🚧 In progress |
| [[Deployment Guide]] | ⏳ Planned |
| [[Migration Guide]] | ⏳ Planned |

---

## Related

- [[SMF Social v1 - Architecture]] (Postiz-based)
- [[SMF Social - System State]]
- [[SMF Social Publisher Roadmap]] (original plan)

---

**Questions?** Document in Obsidian or GitHub issues.
