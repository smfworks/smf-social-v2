#!/bin/bash
# =============================================================================
# SMF Social v2 - OAuth Test Script
# =============================================================================
# Usage: ./scripts/test-oauth.sh [pinterest|linkedin|x]
# =============================================================================

set -e

PLATFORM=${1:-pinterest}

echo "🔧 Testing OAuth for: $PLATFORM"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info()  { echo -e "${BLUE}[INFO]${NC}  $1"; }
print_ok()    { echo -e "${GREEN}[OK]${NC}   $1"; }
print_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
print_err()  { echo -e "${RED}[ERR]${NC}  $1"; }

# Check if backend is running
print_info "Checking if backend is running..."
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    print_err "Backend not running on http://localhost:8000"
    echo "Start it with: cd backend && python main.py"
    exit 1
fi
print_ok "Backend is running"

# Check environment
print_info "Checking environment variables..."
case $PLATFORM in
  pinterest)
    if [ -z "$PINTEREST_CLIENT_ID" ]; then
      print_warn "PINTEREST_CLIENT_ID not set"
      echo "Set it with: export PINTEREST_CLIENT_ID=your_id"
    else
      print_ok "PINTEREST_CLIENT_ID is set"
    fi
    ;;
  linkedin)
    if [ -z "$LINKEDIN_CLIENT_ID" ]; then
      print_warn "LINKEDIN_CLIENT_ID not set"
    else
      print_ok "LINKEDIN_CLIENT_ID is set"
    fi
    ;;
  x)
    if [ -z "$X_API_KEY" ]; then
      print_warn "X_API_KEY not set"
    else
      print_ok "X_API_KEY is set"
    fi
    ;;
  *)
    print_err "Unknown platform: $PLATFORM"
    print_info "Usage: $0 [pinterest|linkedin|x]"
    exit 1
    ;;
esac

echo ""
echo "=========================================="
echo "OAuth Test Ready"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Open http://localhost:3000"
echo "2. Go to Integrations"
echo "3. Click 'Connect' for $PLATFORM"
echo "4. Complete OAuth flow"
echo ""
echo "Monitor backend logs:"
echo "  docker-compose logs -f backend"
echo "  OR"
echo "  tail -f backend/logs/app.log"
