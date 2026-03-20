#!/bin/bash
# Quick test of SMF Social v2 OAuth flow

set -e

echo "🧪 Testing SMF Social v2 OAuth Flow"
echo "=================================="
echo ""

# Check if backend is running
echo "1. Checking backend..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "   ✅ Backend running"
else
    echo "   ❌ Backend not running"
    echo "   Start with: cd backend && python main.py"
    exit 1
fi

# Check test OAuth status
echo ""
echo "2. Checking test OAuth status..."
STATUS=$(curl -s http://localhost:8000/api/auth/test/status)
echo "   Status: $STATUS"

# Test Pinterest connect endpoint
echo ""
echo "3. Testing Pinterest OAuth connect (mock mode)..."
RESPONSE=$(curl -s "http://localhost:8000/api/auth/pinterest/connect?tenant_id=tenant-1&test=true")
echo "   Response: $RESPONSE"

if echo "$RESPONSE" | grep -q "mock_mode"; then
    echo "   ✅ Mock mode working"
    
    # Extract state from URL
    AUTH_URL=$(echo "$RESPONSE" | grep -o '"authorization_url":"[^"]*' | cut -d'"' -f4)
    STATE=$(echo "$AUTH_URL" | grep -o 'state=[^&]*' | cut -d'=' -f2)
    echo "   State: $STATE"
    
    # Simulate callback
    echo ""
    echo "4. Simulating OAuth callback..."
    MOCK_CODE="test-code-$(date +%s)"
    CALLBACK=$(curl -s "http://localhost:8000/api/auth/pinterest/callback?code=$MOCK_CODE&state=$STATE")
    echo "   Callback response: $CALLBACK"
    
    if echo "$CALLBACK" | grep -q '"success":true'; then
        echo "   ✅ OAuth flow complete!"
        echo ""
        echo "5. Checking integration created..."
        INTEGRATIONS=$(curl -s "http://localhost:8000/api/integrations?tenant_id=tenant-1")
        echo "   Integrations: $INTEGRATIONS"
        
        if echo "$INTEGRATIONS" | grep -q "pinterest"; then
            echo ""
            echo "✅ SUCCESS! Test OAuth flow complete."
            echo ""
            echo "Next: Open http://localhost:3000 and try the UI"
        else
            echo "   ⚠️ Integration may not be saved yet"
        fi
    else
        echo "   ❌ Callback failed"
    fi
else
    echo "   ❌ Mock mode not working"
fi

echo ""
echo "=================================="
echo "Test complete."
