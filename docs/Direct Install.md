# Direct Install (Not Recommended)

**Date:** 2026-03-20  
**Status:** For developers only - Docker preferred

---

## ⚠️ Warning

Direct install is **not recommended** for production use. It has:

- Platform-specific issues (PEP 668 on Ubuntu 24.04)
- Python/Node version conflicts
- Manual dependency management
- Harder to reproduce issues

**Use Docker instead:** `docker-compose up -d`

---

## Requirements

- Python 3.11+
- Node.js 18+
- npm or yarn
- SQLite

---

## Backend Setup

### 1. Python Virtual Environment

```bash
cd backend

# Create virtual environment (required for Ubuntu 24.04+)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Create Python Symlink (Ubuntu)

```bash
# Ubuntu uses 'python3', not 'python'
sudo ln -sf $(which python3) /usr/local/bin/python
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit with your settings
```

### 4. Start Backend

```bash
python main.py
```

Or with reload:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure API URL

```bash
# Edit vite.config.ts
# Ensure proxy points to backend:8000
```

### 3. Start Frontend

```bash
npm run dev
```

---

## Common Issues

### "No module named 'flask'"

**Cause:** Python dependencies not installed or wrong Python

**Fix:**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### "python: not found"

**Cause:** Ubuntu uses 'python3' by default

**Fix:**
```bash
sudo ln -sf $(which python3) /usr/local/bin/python
```

### "concurrently: not found"

**Cause:** npm dependencies not installed

**Fix:**
```bash
cd ~/smf-social-v2
npm install
```

### "externally-managed-environment" (PEP 668)

**Cause:** Ubuntu 24.04 blocks system pip

**Fix:** Use virtual environment (see step 1 above) or **use Docker**.

---

## Running Both Services

### Option 1: Concurrently (Recommended for dev)

```bash
cd ~/smf-social-v2
npm run dev
```

This starts both backend and frontend.

### Option 2: Separate Terminals

**Terminal 1:**
```bash
cd backend
source venv/bin/activate
python main.py
```

**Terminal 2:**
```bash
cd frontend
npm run dev
```

---

## Verification

### Check Backend
```bash
curl http://localhost:8000/health
# Should return: {"status": "ok", "version": "2.0.0"}
```

### Check Frontend
Open http://localhost:3000

---

## When to Use Direct Install

Use direct install **only** when:
- ✅ Developing and need hot reload
- ✅ Debugging backend/frontend code
- ✅ Docker is not available
- ✅ Running on resource-constrained system

**For production and testing, always use Docker.**

---

## Migrate to Docker

To switch from direct install to Docker:

```bash
# Stop direct processes
pkill -f "python main.py"
pkill -f "npm run dev"

# Clean up (optional)
rm -rf backend/venv
rm -rf node_modules frontend/node_modules

# Start with Docker
docker-compose up -d --build
```

---

**Questions?** See [Docker Deployment Guide](Docker Deployment.md)
