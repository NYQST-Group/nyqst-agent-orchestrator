#!/bin/bash
# Smoke tests for verifying local development environment is working
# Run this after starting all services to verify the stack is operational

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"

echo "========================================"
echo "  NYQST Intelli Smoke Tests"
echo "========================================"
echo ""

PASS=0
FAIL=0

check() {
  local name="$1"
  local result="$2"
  if [ "$result" -eq 0 ]; then
    echo -e "${GREEN}✓${NC} $name"
    PASS=$((PASS + 1))
  else
    echo -e "${RED}✗${NC} $name"
    FAIL=$((FAIL + 1))
  fi
}

# 1. Backend health check
echo "--- Backend Services ---"
HEALTH=$(curl -s "$BACKEND_URL/api/v1/health" 2>/dev/null || echo "FAILED")
if echo "$HEALTH" | grep -q '"status":"healthy"'; then
  check "Backend health endpoint" 0
else
  check "Backend health endpoint" 1
  echo "  Response: $HEALTH"
fi

# 2. Database connectivity (from health check)
if echo "$HEALTH" | grep -q '"database":{"status":"healthy"'; then
  check "Database connection" 0
else
  check "Database connection" 1
fi

# 3. Storage connectivity (from health check)
if echo "$HEALTH" | grep -q '"storage":{"status":"healthy"'; then
  check "Storage (MinIO) connection" 0
else
  check "Storage (MinIO) connection" 1
fi

# 4. Index service (OpenSearch)
if echo "$HEALTH" | grep -q '"index":{"status":"healthy"'; then
  check "Index (OpenSearch) connection" 0
else
  check "Index (OpenSearch) connection" 1
fi

# 5. Auth - dev bootstrap endpoint
echo ""
echo "--- Authentication ---"
DEV_AUTH=$(curl -s -X POST "$BACKEND_URL/api/v1/auth/dev-bootstrap" \
  -H "Content-Type: application/json" \
  -d '{}' 2>/dev/null || echo "FAILED")

if echo "$DEV_AUTH" | grep -q '"access_token"'; then
  check "Dev auth bootstrap" 0
  TOKEN=$(echo "$DEV_AUTH" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null || echo "")
else
  check "Dev auth bootstrap" 1
  echo "  Response: $DEV_AUTH"
  TOKEN=""
fi

# 6. Auth - verify token works
if [ -n "$TOKEN" ]; then
  ME=$(curl -s "$BACKEND_URL/api/v1/auth/me" \
    -H "Authorization: Bearer $TOKEN" 2>/dev/null || echo "FAILED")
  if echo "$ME" | grep -q '"tenant_id"'; then
    check "Token verification (/auth/me)" 0
  else
    check "Token verification (/auth/me)" 1
    echo "  Response: $ME"
  fi
else
  check "Token verification (/auth/me)" 1
  echo "  Skipped: no token available"
fi

# 7. API - pointers endpoint (requires auth)
echo ""
echo "--- API Endpoints ---"
if [ -n "$TOKEN" ]; then
  POINTERS=$(curl -s "$BACKEND_URL/api/v1/pointers" \
    -H "Authorization: Bearer $TOKEN" 2>/dev/null || echo "FAILED")
  if echo "$POINTERS" | grep -q '^\['; then
    COUNT=$(echo "$POINTERS" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "?")
    check "Pointers API (found $COUNT notebooks)" 0
  else
    check "Pointers API" 1
    echo "  Response: $POINTERS"
  fi
else
  check "Pointers API" 1
  echo "  Skipped: no token available"
fi

# 8. API - sessions endpoint
if [ -n "$TOKEN" ]; then
  SESSION=$(curl -s -X POST "$BACKEND_URL/api/v1/sessions" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"module":"research"}' 2>/dev/null || echo "FAILED")
  if echo "$SESSION" | grep -q '"id"'; then
    check "Sessions API (create)" 0
  else
    check "Sessions API (create)" 1
    echo "  Response: $SESSION"
  fi
else
  check "Sessions API (create)" 1
  echo "  Skipped: no token available"
fi

# 9. Frontend - dev server
echo ""
echo "--- Frontend ---"
FRONTEND=$(curl -s "$FRONTEND_URL" 2>/dev/null || echo "FAILED")
if echo "$FRONTEND" | grep -q '<!doctype html>'; then
  check "Frontend dev server" 0
else
  check "Frontend dev server" 1
fi

# 10. Frontend - static assets
VITE_CLIENT=$(curl -s "$FRONTEND_URL/@vite/client" 2>/dev/null || echo "FAILED")
if echo "$VITE_CLIENT" | grep -q 'import'; then
  check "Vite HMR client" 0
else
  check "Vite HMR client" 1
fi

# Summary
echo ""
echo "========================================"
echo "  Results: ${GREEN}$PASS passed${NC}, ${RED}$FAIL failed${NC}"
echo "========================================"

if [ "$FAIL" -gt 0 ]; then
  echo ""
  echo -e "${YELLOW}Some checks failed. Common fixes:${NC}"
  echo "  - Backend not running? cd to project root and run: make dev"
  echo "  - Docker services down? Run: docker compose up -d"
  echo "  - Frontend not running? cd ui && npm run dev"
  echo ""
  exit 1
fi

echo ""
echo -e "${GREEN}All checks passed!${NC} The development environment is ready."
echo ""
echo "Next steps:"
echo "  1. Open http://localhost:3000/login"
echo "  2. Click 'Demo Login' to authenticate"
echo "  3. Navigate to Research page to test the chat"
exit 0
