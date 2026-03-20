# SMF Social v2 - Sprint Plan: "Off Postiz in 2 Weeks"

**Goal:** Replace Postiz for SMF Works + first paying customer  
**Deadline:** 2026-04-03 (2 weeks from 2026-03-20)  
**Status:** 🚧 In Progress

---

## The Reality: 2 Week Sprint

**What changes from 4-week plan:**
- Cut platforms: Pinterest only (Week 1), LinkedIn + X (Week 2)
- Skip: Instagram, TikTok, YouTube (post-MVP)
- Skip: Multi-user, advanced analytics
- Skip: Video generation integration (keep using scripts)
- Focus: Working > Perfect

---

## Week 1: Core Working (Mar 20-27)

### Day 1-2: Backend Foundation
- [x] Project structure
- [x] SQLite models
- [x] FastAPI + JWT
- [ ] **Pinterest OAuth working**
- [ ] **Can post to Pinterest**

### Day 3-4: Frontend Basics
- [x] React setup
- [ ] **Login page**
- [ ] **Connect Pinterest UI**
- [ ] **Simple composer**

### Day 5-6: Integration + Polish
- [ ] **LinkedIn OAuth + posting**
- [ ] Scheduler wired up
- [ ] Basic error handling

### Day 7: Buffer Day
- [ ] Fix bugs
- [ ] Test end-to-end
- [ ] Deploy to SMF server

**End Week 1:** SMF Works can post to Pinterest + LinkedIn

---

## Week 2: Production (Mar 28 - Apr 3)

### Day 1-3: X Platform (The Hard One)
- [ ] **X OAuth 1.0a using tweepy**
- [ ] **X posting working**
- [ ] Test all 3 platforms together

### Day 4-5: Scheduler + Reliability
- [ ] **APScheduler persistence**
- [ ] Retry logic
- [ ] Logging

### Day 6-7: Customer Ready
- [ ] **Docker Compose finalized**
- [ ] **Setup documentation**
- [ ] First customer onboarding

**End Week 2:** Off Postiz completely

---

## Cut List (Post-MVP)

**Not building in 2 weeks:**
- ❌ Instagram (requires FB Business verification)
- ❌ TikTok
- ❌ YouTube
- ❌ Multi-user (single admin for now)
- ❌ Analytics dashboard
- ❌ Media library UI
- ❌ Calendar view (use list view)
- ❌ Video generation (keep scripts)
- ❌ Image generation (keep scripts)
- ❌ Chrome extension

**Kept:**
- ✅ Pinterest (easiest OAuth)
- ✅ LinkedIn (high value)
- ✅ X (you use it most, use tweepy)
- ✅ Basic scheduler
- ✅ Simple UI
- ✅ Docker deployment

---

## Daily Targets

### Week 1
| Day | Backend | Frontend | Goal |
|-----|---------|----------|------|
| Mon | FastAPI + Pinterest OAuth | Setup | OAuth flow working |
| Tue | Pinterest posting | Login page | Can post to Pinterest |
| Wed | LinkedIn OAuth | Connect UI | Can connect LinkedIn |
| Thu | LinkedIn posting | Composer | Can post to LinkedIn |
| Fri | Scheduler | Post list | Scheduled posts work |
| Sat | Bug fixes | Polish | E2E working |
| Sun | Deploy to SMF | Test | SMF off Postiz (partial) |

### Week 2
| Day | Backend | Frontend | Goal |
|-----|---------|----------|------|
| Mon | Tweepy setup | - | X OAuth research |
| Tue | X OAuth 1.0a | - | Can connect X |
| Wed | X posting | - | Can post to X |
| Thu | Scheduler persistence | Error handling | Reliable scheduling |
| Fri | Retry logic | Logging | Production ready |
| Sat | Docker final | Docs | Deploy ready |
| Sun | Customer test | First customer | Off Postiz completely |

---

## Success Criteria

### Week 1 Done:
- [ ] Can connect Pinterest account
- [ ] Can connect LinkedIn account
- [ ] Can compose and schedule posts
- [ ] Posts publish automatically

### Week 2 Done:
- [ ] X working
- [ ] All 3 platforms posting
- [ ] SMF Works migrated off Postiz
- [ ] First customer can deploy

---

## Risk Mitigation

### X OAuth Too Hard?
**Mitigation:** Use `tweepy` library - handles OAuth 1.0a
**Fallback:** If X takes >2 days, keep Postiz for X only temporarily

### Time Running Out?
**Cut in order:**
1. Skip X (keep Postiz for it)
2. Skip LinkedIn (Pinterest MVP)
3. Manual scheduling (no automation)

### Customer Needs Instagram?
**Response:** "Coming Week 3" - Pinterest/LinkedIn/X sufficient for most SMBs initially

---

## Revenue Accelerated

**Timeline:**
- Week 1: You save $20-50/mo (Postiz cancelled)
- Week 2: First customer at $50-100/mo

**Goal:** Pay for development time within 2 months

---

## Today (Mar 20)

**Priority order:**
1. Pinterest OAuth working (4 hours)
2. Login page (2 hours)
3. Connect Pinterest UI (2 hours)

**End of day:** OAuth callback successful, tokens stored

---

## The Mantra

**"Perfect is the enemy of shipped."**

- Working > Pretty
- 3 platforms > 6 platforms broken
- Ship Friday > Perfect Sunday

---

**Last updated:** 2026-03-20  
**Sprint ends:** 2026-04-03 (2 weeks)
