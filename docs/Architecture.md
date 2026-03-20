# SMF Social v2 - Architecture

**Version:** 2.0  
**Date:** 2026-03-20  
**Status:** In Development

---

## System Overview

SMF Social v2 is a **multi-tenant, self-hostable** social media automation platform. Unlike v1 (which leverages Postiz SaaS), v2 is a complete standalone solution.

### Key Design Principles

1. **Customer-Owned OAuth** - Each customer creates their own OAuth apps on social platforms
2. **Data Isolation** - Complete tenant separation at database level
3. **Flexible Deployment** - Self-hosted or SaaS model
4. **Platform Native** - Direct API calls to social platforms (no middleware)
5. **Sustainable** - Built to last, not dependent on third-party services

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                       CLIENT LAYER                               │
├─────────────────────────────────────────────────────────────────┤
│  React SPA (Vite)                                                │
│  ├── OAuth Connection Flows                                      │
│  ├── Post Composer                                               │
│  ├── Content Calendar                                            │
│  └── Analytics Dashboard                                         │
└──────────────────────┬──────────────────────────────────────────┘
                       │ HTTPS
┌──────────────────────▼──────────────────────────────────────────┐
│                      API LAYER                                 │
├────────────────────────────────────────────────────────────────┤
│  FastAPI (Python)                                               │
│  ├── Auth Routes                                                │
│  │   ├── /auth/login                                            │
│  │   ├── /auth/{platform}/connect ← OAuth redirect            │
│  │   └── /auth/{platform}/callback ← OAuth callback           │
│  ├── Integration Routes                                         │
│  │   ├── GET    /integrations                                 │
│  │   ├── DELETE /integrations/{id}                            │
│  │   └── GET    /integrations/{platform}/boards               │
│  ├── Post Routes                                                │
│  │   ├── POST   /posts                                          │
│  │   ├── GET    /posts                                          │
│  │   ├── PATCH  /posts/{id}                                     │
│  │   └── POST   /posts/{id}/publish                             │
│  └── Media Routes                                               │
│      └── POST   /media/upload                                   │
└──────────────────────┬──────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│                   SERVICE LAYER                                │
├────────────────────────────────────────────────────────────────┤
│  Business Logic                                                 │
│  ├── OAuthService                                               │
│  │   ├── initiate_oauth_flow(platform, tenant_id)               │
│  │   ├── handle_callback(platform, code, state)                 │
│  │   └── refresh_token(integration_id)                          │
│  ├── PostService                                                │
│  │   ├── create_post(tenant_id, content, platforms)             │
│  │   ├── schedule_post(post_id, scheduled_for)                  │
│  │   └── publish_post(post_id)                                  │
│  ├── MediaService                                               │
│  │   ├── upload_media(file, tenant_id)                          │
│  │   └── upload_to_platform(media_id, platform)                 │
│  └── EncryptionService                                          │
│      ├── encrypt_token(plain_text)                                │
│      └── decrypt_token(cipher_text)                               │
└──────────────────────┬──────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│                  PROVIDER LAYER                              │
├────────────────────────────────────────────────────────────────┤
│  Platform Implementations                                     │
│  ├── BaseProvider (abstract)                                  │
│  ├── PinterestProvider (OAuth 2.0) ⭐ Phase 1                │
│  ├── LinkedInProvider (OAuth 2.0)  ⭐ Phase 1                │
│  ├── XProvider (OAuth 1.0a)      🚧 Phase 2                │
│  ├── InstagramProvider             🚧 Phase 2                │
│  └── TikTokProvider                🚧 Phase 3                │
└──────────────────────┬──────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│                   SCHEDULER LAYER                              │
├────────────────────────────────────────────────────────────────┤
│  APScheduler (Python)                                           │
│  ├── Job Store: SQLAlchemy (PostgreSQL)                       │
│  ├── Executor: ThreadPool                                       │
│  ├── Job: publish_scheduled_post(post_id)                       │
│  └── Retry: Exponential backoff (2s, 4s, 8s...)               │
└──────────────────────┬──────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│                   DATA LAYER                                   │
├────────────────────────────────────────────────────────────────┤
│  PostgreSQL (Multi-tenant)                                    │
│  ├── tenants                                                    │
│  │   └── id, name, slug, settings, is_active                    │
│  ├── oauth_apps                                                 │
│  │   └── tenant_id, platform, client_id, client_secret        │
│  ├── integrations                                               │
│  │   └── tenant_id, platform, access_token (encrypted)          │
│  ├── posts                                                      │
│  │   └── tenant_id, content, status, scheduled_for             │
│  └── media                                                      │
│      └── tenant_id, file_path, platform_media_id               │
└────────────────────────────────────────────────────────────────┘
```

---

## Single-Tenant Design (Current Model)

### Deployment Model

**Single-Tenant per Customer (Self-Hosted Docker)**

Each customer gets a **dedicated Docker deployment** on their own infrastructure:

```yaml
# One deployment per customer
# Customer owns: server, database, OAuth apps, data

deployment:
  customer: "ACME Corp"
  host: "social.acme.com" or "acme.com/social"
  
  services:
    - postgres (dedicated instance)
    - backend (single tenant)
    - frontend (single tenant)
    - nginx
    
  data_isolation: "complete"
  oauth_strategy: "customer creates their own apps"
  maintenance: "customer or SMF managed"
```

### Why Single-Tenant (For Now)

**Advantages:**
- ✅ Complete data isolation (security, compliance)
- ✅ Customer owns their infrastructure
- ✅ No rate limit sharing between customers
- ✅ Simpler architecture (no multi-tenant complexity)
- ✅ Easier debugging and support
- ✅ Customer can customize if needed

**Trade-offs:**
- Higher resource usage (dedicated DB per customer)
- More complex deployments
- Slower to onboard new customers
- Higher maintenance overhead

### Future: Multi-Tenant SaaS (Optional)

**When to consider:**
- 50+ customers
- SMB market (price-sensitive)
- Need rapid onboarding

**Migration path:**
- Keep single-tenant for enterprise
- Add multi-tenant tier for SMBs
- Customer choice at signup

### Tenant Isolation (Even in Single-Tenant)

Even with single-tenant deployments, we keep `tenant_id` in schema for:
1. Future multi-tenant option
2. Multi-user within one customer
3. Testing environments

```python
# Single-tenant: tenant_id is always the same
posts = db.query(Post).filter(Post.tenant_id == "acme-corp").all()

# Multi-user within tenant:
posts = db.query(Post).filter(Post.user_id == current_user.id).all()
```

---

## OAuth Flow Architecture

### OAuth 2.0 (Pinterest, LinkedIn)

```
┌─────────┐                                    ┌──────────┐
│  User   │───1. Click "Connect Pinterest"────>│ Frontend │
└─────────┘                                    └────┬─────┘
                                                    │
                                                    │ 2. POST /auth/pinterest/connect
                                                    │    {tenant_id, redirect_uri}
                                                    │
                                               ┌────▼──────┐
                                               │  Backend  │
                                               │  - Verify tenant
                                               │  - Get OAuth app creds
                                               │  - Generate state
                                               └────┬──────┘
                                                    │
                                                    │ 3. Return Pinterest auth URL
                                                    │
┌─────────┐                                    ┌────▼──────┐
│  User   │───4. Authorize SMF app on Pinterest───>│ Pinterest │
└─────────┘                                    └────┬──────┘
                                                    │
                                                    │ 5. Redirect to callback
                                                    │    ?code=xxx&state=yyy
                                                    │
                                               ┌────▼──────┐
                                               │  Frontend │
                                               │  /auth/pinterest/callback
                                               └────┬──────┘
                                                    │
                                                    │ 6. POST /auth/pinterest/callback
                                                    │    {code, state}
                                                    │
                                               ┌────▼──────┐
                                               │  Backend  │
                                               │  - Exchange code for tokens
                                               │  - Encrypt tokens
                                               │  - Save to database
                                               │  - Return success
                                               └───────────┘
```

### OAuth 1.0a (X/Twitter)

More complex three-legged flow with request token, authorization, and access token exchange.

---

## Security Model

### Token Encryption

OAuth tokens are **encrypted at rest** using AES-256:

```python
from cryptography.fernet import Fernet

class EncryptionService:
    def __init__(self, master_key: str):
        self.cipher = Fernet(master_key)
    
    def encrypt_token(self, plain_text: str) -> str:
        return self.cipher.encrypt(plain_text.encode()).decode()
    
    def decrypt_token(self, cipher_text: str) -> str:
        return self.cipher.decrypt(cipher_text.encode()).decode()
```

### API Security

- **JWT Authentication** for API access
- **Rate limiting** per tenant per endpoint
- **Input validation** on all endpoints
- **CORS** configured for frontend origin only
- **HTTPS only** in production

### Secrets Management

- OAuth app credentials: Database (encrypted)
- User tokens: Database (encrypted)
- Master encryption key: Environment variable
- Database credentials: Environment variable
- No secrets in code or Git

---

## Platform Implementation Details

### Pinterest (Phase 1 - Easiest)

**Why first:**
- OAuth 2.0 (standard)
- Simple REST API
- Clear documentation
- Fast to implement

**Implementation:**
- ✅ Authorization URL generation
- ✅ Token exchange
- ✅ User info fetching
- ✅ Pin creation
- ✅ Board listing
- ⚠️ Media upload (requires Pinterest CDN)

### LinkedIn (Phase 1 - High Value)

**Why second:**
- OAuth 2.0
- B2B focus (matches SMF audience)
- Good API documentation
- Share/repost features

**Implementation:**
- ✅ OAuth flow
- ⚠️ UGC Posts API (complex JSON-LD format)
- ⚠️ Media upload (multi-step)
- ⚠️ Company page vs personal profile

### X (Phase 2 - Hardest)

**Why delayed:**
- OAuth 1.0a (complex signature generation)
- Rate limiting is strict
- API v2 migration complexity
- Requires media upload before posting

**Implementation:**
- 🚧 OAuth 1.0a request signing
- 🚧 Request token flow
- 🚧 Media upload endpoints
- 🚧 Tweet threading
- 🚧 Rate limit handling

**Recommendation:** Use `tweepy` library in production

### Instagram (Phase 2 - Moderate)

**Challenges:**
- Requires Facebook Business verification
- Business/Creator account required
- Graph API complexity
- Stories vs posts vs reels

### TikTok (Phase 3 - Moderate)

**Features:**
- Video-focused API
- OAuth 2.0
- Content Publishing API

### YouTube (Phase 3 - Moderate)

**Features:**
- Google OAuth
- Video uploads
- Playlist management

---

## Database Schema

See [[Database Schema]] for full details.

### Key Tables

| Table | Purpose |
|-------|---------|
| `tenants` | Customer isolation |
| `oauth_apps` | Platform app credentials per tenant |
| `integrations` | User tokens (encrypted) per platform |
| `posts` | Scheduled and published content |
| `media` | Uploaded assets |
| `users` | Admin users per tenant |

---

## Scheduler Architecture

### APScheduler

Embedded scheduler (no separate service needed):

```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

# Schedule a post
scheduler.add_job(
    func=publish_post,
    trigger='date',
    run_date=post.scheduled_for,
    args=[post.id],
    id=f'post_{post.id}',
    replace_existing=True
)

# Retry on failure
@retry(max_attempts=3, delay=2, backoff=2)
def publish_post(post_id: str):
    post = get_post(post_id)
    provider = get_provider(post.platform)
    provider.post(post.content, post.access_token)
```

### Alternative: BullMQ

If we need distributed queue (multiple workers):

```yaml
# docker-compose.yml
services:
  redis:
    image: redis:alpine
  
  scheduler:
    build: .
    command: python -m smf.scheduler.worker
    depends_on:
      - redis
      - postgres
```

**Decision:** Start with APScheduler (embedded), move to Redis/Celery if scale requires.

---

## Frontend Architecture

### Technology Stack

- **Framework:** React 18+
- **Build Tool:** Vite
- **Styling:** Tailwind CSS
- **State:** React Query (TanStack Query) + Zustand
- **Router:** React Router
- **Forms:** React Hook Form
- **UI Library:** Headless UI + custom components

### Page Structure

```
/
├── /login                    # Tenant login
├── /dashboard                # Overview, recent activity
├── /integrations             # Connect/manage social accounts
│   └── /:platform/connect   # OAuth redirect handling
├── /composer                 # Create posts
├── /calendar                 # Content calendar
├── /posts                    # List/history
├── /analytics                # Performance metrics
├── /settings                 # Tenant settings
│   └── /oauth-apps          # Configure OAuth credentials
└── /media                    # Media library
```

### Key Components

- `PlatformCard` - Show connection status
- `PostComposer` - Create/edit posts
- `MediaUploader` - Upload images/videos
- `CalendarGrid` - Visual calendar
- `AnalyticsChart` - Metrics visualization

---

## Deployment Architecture

### Docker Compose (Self-Hosted)

```yaml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: smf_social
      POSTGRES_USER: smf
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  backend:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://smf:${DB_PASSWORD}@postgres:5432/smf_social
      - ENCRYPTION_KEY=${ENCRYPTION_KEY}
      - JWT_SECRET=${JWT_SECRET}
    depends_on:
      - postgres
  
  frontend:
    build: ./frontend
    environment:
      - VITE_API_URL=/api
    depends_on:
      - backend
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - backend
      - frontend
```

### Kubernetes (SaaS)

For multi-tenant SaaS deployment with scaling.

---

## Development Roadmap

### Phase 1: Foundation (Weeks 1-3)
- [x] Project structure
- [x] Database models
- [x] Base provider class
- [ ] FastAPI setup
- [ ] JWT authentication
- [ ] Pinterest OAuth flow
- [ ] Pinterest posting API
- [ ] React frontend skeleton
- [ ] Integration connection UI

### Phase 2: Core Features (Weeks 4-6)
- [ ] LinkedIn OAuth + posting
- [ ] Media upload handling
- [ ] Post scheduler (APScheduler)
- [ ] Content composer
- [ ] Calendar view
- [ ] Basic analytics

### Phase 3: Scale (Weeks 7-8)
- [ ] X OAuth 1.0a
- [ ] Instagram connection
- [ ] TikTok/YouTube
- [ ] Error handling + retries
- [ ] Rate limiting
- [ ] Documentation

### Phase 4: Polish (Weeks 9-10)
- [ ] Customer onboarding flow
- [ ] Admin dashboard
- [ ] Analytics dashboard
- [ ] Multi-user support
- [ ] Testing + QA

---

## Comparison: v1 vs v2

| Aspect | v1 (Postiz) | v2 (Standalone) |
|--------|-------------|-----------------|
| **OAuth** | Postiz handles | Customer creates apps |
| **Tokens** | Postiz stores | Encrypted in our DB |
| **Rate limits** | Shared | Per-customer |
| **Deployment** | N/A | Self-hosted or SaaS |
| **Data** | N/A | Customer-owned |
| **Branding** | Postiz branding | Full white-label |
| **Development time** | 2 days | 8-10 weeks |
| **Maintenance** | Low | Higher (OAuth refresh) |

---

## Migration Strategy

### From v1 to v2 (SMF Works)

1. **Preparation** (Week 8)
   - Export scheduled posts from v1
   - Document which integrations are active

2. **Parallel Running** (Weeks 9-10)
   - Set up v2 with new OAuth apps
   - Connect platforms to v2
   - Run both systems
   - New posts → v2
   - Existing posts → v1 completes

3. **Switchover** (Week 11)
   - Update scripts to use v2 API
   - DNS/subdomain switch
   - Monitor for 1 week

4. **Sunset** (Week 12+)
   - Cancel Postiz subscription
   - Archive v1 code
   - Document migration for future customers

---

## Documentation

- [[SMF Social v2 - README]]
- [[Database Schema]]
- [[API Reference]] (TODO)
- [[OAuth Setup Guide]] (TODO)
- [[Deployment Guide]] (TODO)
- [[Migration Guide]] (TODO)

---

**Last updated:** 2026-03-20  
**Next review:** Weekly during development
