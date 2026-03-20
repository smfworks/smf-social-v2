# SMF Social v2 - Sprint Plan: "Off Postiz in 4 Weeks"

**Goal:** Replace Postiz for SMF Works + ready for first paying customer  
**Deadline:** 2026-04-17 (4 weeks from 2026-03-20)  
**Status:** 🚧 In Progress

---

## Week 1: Foundation (Mar 20-27)

### Backend
- [x] Project structure
- [x] SQLite models
- [x] Base provider class
- [ ] **FastAPI setup with JWT auth**
- [ ] **Pinterest OAuth + posting (MVP platform)**
- [ ] Encryption service for tokens

### Frontend
- [x] React project setup
- [ ] **Login page**
- [ ] **Integration connection UI (Pinterest)**
- [ ] Basic layout shell

### DevOps
- [ ] Docker Compose for local dev
- [ ] Environment variable setup

**Deliverable:** Can connect Pinterest account and post manually via API

---

## Week 2: Core Features (Mar 28 - Apr 3)

### Backend
- [ ] **LinkedIn OAuth + posting**
- [ ] **X OAuth 1.0a + posting** (use tweepy library)
- [ ] **Scheduler (APScheduler)**
- [ ] Post CRUD API
- [ ] Media upload handling

### Frontend
- [ ] **Post composer**
- [ ] **Content calendar view**
- [ ] **Integration management**
- [ ] Media upload

### Priority: SMF Works Platforms
Your current Postiz channels:
1. **X** - Highest priority (you post here most)
2. **LinkedIn** - High value
3. **Pinterest** - Easiest to implement
4. **Instagram** - Medium (requires FB)
5. **TikTok** - Medium
6. **YouTube** - Lower priority

**Deliverable:** Can schedule posts to X, LinkedIn, Pinterest

---

## Week 3: Polish + Instagram (Apr 4-10)

### Backend
- [ ] **Instagram OAuth + posting**
- [ ] Error handling + retry logic
- [ ] Rate limit protection
- [ ] Token refresh automation
- [ ] Basic analytics (post status tracking)

### Frontend
- [ ] **Posts list/history**
- [ ] **Analytics dashboard** (simple)
- [ ] Error notifications
- [ ] Mobile responsive polish

### Documentation
- [ ] Customer setup guide
- [ ] OAuth app creation instructions
- [ ] Deployment guide

**Deliverable:** Full replacement for SMF Works current Postiz usage

---

## Week 4: Customer-Ready (Apr 11-17)

### Backend
- [ ] **Multi-user support** (admin vs editor roles)
- [ ] Tenant onboarding API
- [ ] Health checks
- [ ] Logging and monitoring

### Frontend
- [ ] **Settings page**
- [ ] User management (if multi-user)
- [ ] Final UI polish

### DevOps
- [ ] **Docker production build**
- [ ] **Environment setup script**
- [ ] Backup/restore documentation

### Sales Prep
- [ ] **Pricing page** (website)
- [ ] **Demo video/script**
- [ ] **First customer onboarding checklist**

**Deliverable:** Production-ready for first paying customer

---

## Cut Scope (Post-MVP)

**Won't build in Week 1-4:**
- ❌ TikTok (can add Week 5)
- ❌ YouTube (can add Week 5)
- ❌ Advanced analytics
- ❌ AI content generation (keep using current Python scripts)
- ❌ Chrome extension
- ❌ Mobile app
- ❌ Multi-tenant SaaS (keep single-tenant for now)
- ❌ Payment processing (invoice manually)

**Will leverage existing:**
- ✅ Image generation (`image_generator.py`)
- ✅ Video generation (`generate_video_shorts.py`)
- Integrate these into v2 workflows

---

## Daily Standup Template

**What I completed:**
- 

**What I'm working on:**
- 

**Blockers:**
- 

**ETA for current task:**
- 

---

## Success Criteria

### Week 1 Done When:
- [ ] Can run `docker-compose up` and app loads
- [ ] Can log in with test user
- [ ] Can connect Pinterest OAuth
- [ ] Can post to Pinterest via API

### Week 2 Done When:
- [ ] X, LinkedIn, Pinterest all posting
- [ ] Can schedule posts for future
- [ ] Scheduler actually publishes on time
- [ ] Basic composer UI works

### Week 3 Done When:
- [ ] SMF Works can migrate off Postiz
- [ ] Instagram working
- [ ] All current Postiz features replaced

### Week 4 Done When:
- [ ] First customer can self-deploy
- [ ] Documentation complete
- [ ] Ready for paid deployment

---

## Risk Mitigation

### OAuth Complexity (High Risk)
**X OAuth 1.0a is hardest:**
- Mitigation: Use `tweepy` library
- Fallback: Delay X to Week 3, build others first
- Workaround: Keep Postiz for X only temporarily

### Time Constraints (Medium Risk)
**If falling behind:**
- Cut TikTok, YouTube completely (Week 5+)
- Skip Instagram if needed (SMF less active there)
- Manual onboarding vs automated (Week 1 customer)

### Technical Blockers (Low Risk)
**Platform API changes:**
- Mitigation: Test early, often
- Fallback: Platform status monitoring
- Contingency: Keep Postiz as backup during transition

---

## Revenue Projection

### Cost Savings (You)
- Postiz cost: ~$20-50/month
- Your savings: $300-600/year

### Revenue Potential
- Target price: $50-100/month per customer
- First customer: Month 2 (April 2026)
- Goal: 10 customers by end of 2026 = $6,000-12,000/year

---

## Today's Priority (Mar 20)

1. **FastAPI backend skeleton** (2 hours)
   - Main app, JWT auth, health check
   
2. **Pinterest OAuth flow** (2 hours)
   - Connect endpoint
   - Callback handler
   - Token storage

3. **React frontend skeleton** (2 hours)
   - Login page
   - Integration connection UI
   - Basic layout

**End of day:** Working dev environment, can connect Pinterest

---

## Notes

- **Speed > Perfection** — working beats polished
- **Test with real accounts** — not just mocks
- **Document as we go** — not after
- **Customer feedback > assumptions** — deploy to SMF Works early

---

## Related

- [[SMF Social v2 - Architecture]]
- [[SMF Social v2 - README]]
- Current status: v1 (Postiz) still running, v2 under development

---

**Last updated:** 2026-03-20  
**Next review:** Daily
