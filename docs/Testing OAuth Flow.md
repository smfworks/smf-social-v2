# Testing SMF Social v2 OAuth Flow

**Date:** 2026-03-20  
**Purpose:** Verify OAuth integration works without real credentials

---

## Quick Start (Automated Test)

Run the automated test script:

```bash
cd ~/smf-social-v2
./scripts/quick-test.sh
```

This will:
1. Check backend is running
2. Test OAuth connect endpoint
3. Simulate OAuth callback
4. Verify integration created

**Expected output:**
```
🧪 Testing SMF Social v2 OAuth Flow
==================================

1. Checking backend...
   ✅ Backend running

2. Checking test OAuth status...
   Status: {"mock_mode_globally_enabled": false, ...}

3. Testing Pinterest OAuth connect (mock mode)...
   ✅ Mock mode working

4. Simulating OAuth callback...
   ✅ OAuth flow complete!

5. Checking integration created...
   ✅ SUCCESS! Test OAuth flow complete.

Next: Open http://localhost:3000 and try the UI
```

---

## Manual Testing via UI

### 1. Start Services

**Terminal 1 - Backend:**
```bash
cd ~/smf-social-v2/backend
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd ~/smf-social-v2/frontend
npm run dev
```

### 2. Open Web Interface

Navigate to: http://localhost:3000

### 3. Go to Integrations

Click "Integrations" in the left sidebar.

### 4. Enable Test Mode

You should see a **yellow banner** at the top:
```
Test Mode: [Toggle] Using mock OAuth (no real credentials needed)
```

Make sure the toggle is **ON** (blue).

### 5. Connect Pinterest (Test)

Click the **"Connect (Test)"** button on the Pinterest card.

The button will show a spinner for ~2 seconds while it:
1. Generates mock OAuth URL
2. Simulates user authorization
3. Creates test integration

### 6. Verify Success

You should see:
- ✅ Alert: "Test OAuth successful! Connected as @testuser"
- Pinterest card now shows: "Connected"
- Account name: "@testuser"
- Profile picture placeholder

---

## What Test Mode Does

**Backend (api/auth.py):**
- Detects `?test=true` parameter
- Generates fake OAuth URL
- Simulates token exchange
- Creates real database record with test data

**Frontend (Integrations.tsx):**
- Shows toggle for test/real mode
- Yellow "Connect (Test)" button
- Auto-handles mock callback
- No external redirect needed

**Database:**
- Real `Integration` record created
- Encrypted test tokens
- Associated with `tenant-1`

---

## Testing Real OAuth (With Credentials)

### 1. Get Real Credentials

**Pinterest:**
1. Go to https://developers.pinterest.com/apps/
2. Click "Create App"
3. Fill in app details
4. Copy Client ID and Secret

### 2. Set Environment Variables

```bash
export PINTEREST_CLIENT_ID="your_real_client_id"
export PINTEREST_CLIENT_SECRET="your_real_client_secret"
```

Or edit `~/.openclaw/secrets/smf-social.env`:
```
PINTEREST_CLIENT_ID=your_real_client_id
PINTEREST_CLIENT_SECRET=your_real_client_secret
```

### 3. Disable Test Mode

In the web UI:
- Toggle **Test Mode OFF**
- Button changes to "Connect" (blue)

### 4. Connect

Click **"Connect"** button.

This will:
1. Redirect to Pinterest authorization page
2. Ask you to approve the app
3. Redirect back to SMF Social
4. Show "Connected" with real account info

---

## Troubleshooting

### "Backend not running"

```bash
cd ~/smf-social-v2/backend
python main.py
```

Check logs: `tail -f logs/app.log`

### "Mock mode not working"

Check backend console for errors.

Verify endpoint manually:
```bash
curl "http://localhost:8000/api/auth/pinterest/connect?tenant_id=tenant-1&test=true"
```

Should return JSON with `mock_mode: true`.

### "Integration not showing"

Refresh the page after connecting.

Check database:
```bash
cd ~/smf-social-v2/backend
python -c "from core.database import get_db; from models.sqlite_database import Integration; db = next(get_db()); print(db.query(Integration).all())"
```

### "Test mode toggle not showing"

Make sure you pulled latest code:
```bash
git pull origin master
```

---

## API Endpoints

### Check Test Status
```bash
curl http://localhost:8000/api/auth/test/status
```

### Connect (Mock)
```bash
curl "http://localhost:8000/api/auth/pinterest/connect?tenant_id=tenant-1&test=true"
```

### Connect (Real)
```bash
curl "http://localhost:8000/api/auth/pinterest/connect?tenant_id=tenant-1"
```

### List Integrations
```bash
curl "http://localhost:8000/api/integrations?tenant_id=tenant-1"
```

---

## Test vs Real Mode Comparison

| Feature | Test Mode | Real Mode |
|---------|-----------|-----------|
| Credentials | Fake/mocked | Real OAuth app |
| External redirect | No | Yes |
| User approval | Simulated | Required |
| Posting | Simulated | Real |
| Rate limits | None | Platform limits |
| Use case | Development | Production |

---

## Next Steps After Testing

1. **Verify flow works** ✅ (you are here)
2. **Create real OAuth apps** (Pinterest, LinkedIn, X)
3. **Add credentials** (env vars or UI)
4. **Test real posting** (create post → publish)
5. **Verify scheduling** (APScheduler)

---

**Questions?**
- Check logs: `docker-compose logs -f backend` or `tail -f backend/logs/*.log`
- API docs: See inline comments in `backend/api/auth.py`
