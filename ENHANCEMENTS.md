# RingCentral Gateway v2.0 - Enhancements Documentation

## 🚀 What's New in v2.0

This major release transforms the RingCentral Gateway from a basic extension management tool into a **production-grade, enterprise-ready telephony automation platform**.

---

## ✨ New Features

### 1. **Advanced Resilience & Reliability**

#### Rate Limit Handling with Exponential Backoff
- Automatic detection of 429 rate limit responses
- Intelligent retry logic with exponential backoff (2s → 4s → 8s)
- Respects `Retry-After` headers from RingCentral API
- Configurable retry attempts (default: 3)

```python
# Automatically handles rate limits - no code changes needed!
response = await client.get("/restapi/v1.0/account/~/extension")
```

#### Circuit Breaker Pattern
- Prevents cascading failures during RingCentral API outages
- Opens circuit after 5 consecutive failures
- 60-second cooldown period before retry attempts
- Automatic recovery when API becomes healthy

```python
# app/clients/ringcentral.py:34-57
class RingCentralClient:
    _circuit_breaker_failures = 0
    _circuit_breaker_threshold = 5
    _circuit_breaker_timeout = 60
```

---

### 2. **Webhook & Event Processing System**

#### Webhook Subscription Management
Create and manage RingCentral webhook subscriptions programmatically:

```http
POST /api/webhooks/subscriptions
Content-Type: application/json

{
  "eventFilters": [
    "/restapi/v1.0/account/~/extension/~/message-store",
    "/restapi/v1.0/account/~/extension/~/presence"
  ],
  "deliveryMode": {
    "transportType": "WebHook",
    "address": "https://your-domain.com/api/webhooks/events"
  }
}
```

#### Webhook Validation
- HMAC-SHA256 signature validation
- Validation token exchange
- Automatic event routing

```http
POST /api/webhooks/events
Content-Type: application/json

{
  "uuid": "abc-123",
  "event": "/restapi/v1.0/account/~/extension/~/message-store",
  "timestamp": "2025-10-01T10:00:00Z",
  "subscriptionId": "sub-456",
  "body": { ... }
}
```

**Available Endpoints:**
- `POST /api/webhooks/subscriptions` - Create subscription
- `GET /api/webhooks/subscriptions` - List subscriptions
- `POST /api/webhooks/validate` - Validate webhook
- `POST /api/webhooks/events` - Receive events

---

### 3. **Call Queue Management**

Full CRUD operations for RingCentral call queues:

```http
# Create call queue
POST /api/call-queues
{
  "name": "Customer Support",
  "extensionNumber": "5000",
  "members": [
    {"id": "101", "extensionNumber": "101"},
    {"id": "102", "extensionNumber": "102"}
  ]
}

# List all call queues
GET /api/call-queues?page=1&perPage=50

# Get specific queue
GET /api/call-queues/{queue_id}

# Update queue
PUT /api/call-queues/{queue_id}

# Delete queue
DELETE /api/call-queues/{queue_id}
```

---

### 4. **Phone Number Provisioning**

Search and manage phone numbers:

```http
# Search available numbers by area code
GET /api/phone-numbers/available?areaCode=650&countryId=1&perPage=10

# List account phone numbers
GET /api/phone-numbers?page=1&perPage=100
```

**Response:**
```json
{
  "records": [
    {
      "phoneNumber": "+16505551234",
      "type": "VoiceOnly",
      "usageType": "DirectNumber",
      "features": ["CallerId"],
      "status": "Normal"
    }
  ]
}
```

---

### 5. **Analytics & Reporting**

#### Call Detail Records (CDR)
```http
# Get account-wide call logs
GET /api/analytics/call-logs?page=1&perPage=100&direction=Inbound

# Get extension-specific call logs
GET /api/analytics/call-logs/extension/{extension_id}?dateFrom=2025-10-01

# Get specific call record
GET /api/analytics/call-logs/{record_id}
```

**Call Log Fields:**
- Session ID and call duration
- Direction (Inbound/Outbound)
- Call result and action
- From/To information
- Recording links (if available)

---

### 6. **Observability & Monitoring**

#### Prometheus Metrics
Exposed at `/metrics` endpoint:

**HTTP Metrics:**
- `http_requests_total` - Total requests by method, endpoint, status
- `http_request_duration_seconds` - Request latency histogram
- `http_requests_in_progress` - Concurrent requests gauge

**RingCentral API Metrics:**
- `ringcentral_api_calls_total` - API calls by endpoint and status
- `ringcentral_api_duration_seconds` - API call latency
- `circuit_breaker_failures` - Current failure count
- `rate_limit_hits_total` - Rate limit encounters

#### Structured JSON Logging
```json
{
  "timestamp": "2025-10-01T10:00:00.123Z",
  "logger": "app.clients.ringcentral",
  "level": "INFO",
  "request_id": "abc-123-def-456",
  "message": "Request completed",
  "method": "GET",
  "path": "/api/users",
  "status_code": 200,
  "duration_ms": 245.67
}
```

**Features:**
- Automatic request ID generation
- Request/response logging
- Error tracking with stack traces
- Performance metrics per request

---

### 7. **Production Deployment**

#### Docker Support
```bash
# Build and run with Docker
docker build -t rc-gateway:2.0 .
docker run -p 8000:8000 -v ./config:/app/config rc-gateway:2.0
```

#### Docker Compose Stack
Full observability stack included:

```bash
docker-compose up -d
```

**Includes:**
- **API Service** (port 8000) - Main RingCentral Gateway
- **Redis** (port 6379) - Caching and session storage
- **Prometheus** (port 9090) - Metrics collection
- **Grafana** (port 3000) - Metrics visualization

**Access Dashboards:**
- API: http://localhost:8000/docs
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)
- Metrics: http://localhost:8000/metrics

---

## 📊 Architecture Changes

### Before (v1.0)
```
Client → FastAPI → RingCentral Client → RingCentral API
```

### After (v2.0)
```
Client
  ↓
Logging Middleware (Request ID, Structured Logs)
  ↓
Metrics Middleware (Prometheus)
  ↓
FastAPI Routes (Extensions, Sites, Webhooks, Queues, Numbers, Analytics)
  ↓
Service Layer (Business Logic)
  ↓
Enhanced RingCentral Client (Rate Limits, Circuit Breaker, Retries)
  ↓
RingCentral API
```

---

## 🔧 Configuration

### New Environment Variables

```bash
# Redis Configuration (optional)
REDIS_URL=redis://localhost:6379

# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR

# Circuit Breaker
CIRCUIT_BREAKER_THRESHOLD=5
CIRCUIT_BREAKER_TIMEOUT=60

# Rate Limiting
RATE_LIMIT_RETRY_ATTEMPTS=3
RATE_LIMIT_BACKOFF_MULTIPLIER=1
```

---

## 📈 Performance Improvements

| Metric | v1.0 | v2.0 | Improvement |
|--------|------|------|-------------|
| Rate limit handling | Manual | Automatic | 100% |
| API failure recovery | None | Circuit breaker | ∞ |
| Request retry | Manual | Auto (3x) | 100% |
| Observability | None | Full stack | ∞ |
| Webhook support | None | Complete | ∞ |
| Call queue mgmt | None | Full CRUD | ∞ |
| Analytics | None | CDR + Metrics | ∞ |

---

## 🚀 Getting Started with v2.0

### Quick Start
```bash
# 1. Install new dependencies
pip install -r requirements.txt

# 2. Run with Docker Compose (recommended)
docker-compose up -d

# 3. Or run standalone
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 4. Explore new APIs
open http://localhost:8000/docs

# 5. Check metrics
open http://localhost:8000/metrics
```

### Migration from v1.0

**Good news:** v2.0 is **100% backward compatible**! All v1.0 endpoints work unchanged.

**New capabilities automatically active:**
- ✅ Rate limit handling - Just works
- ✅ Circuit breaker - Automatic protection
- ✅ Structured logging - Enabled by default
- ✅ Metrics export - Available at `/metrics`

**To use new features:**
1. No code changes needed for existing endpoints
2. New endpoints available immediately
3. Webhook setup requires configuration
4. Docker deployment recommended for production

---

## 📝 API Summary

### v1.0 Endpoints (Unchanged)
- ✅ `GET /api/health` - Health check
- ✅ `GET /api/extensions` - List extensions
- ✅ `POST /api/extensions` - Create extension
- ✅ `GET /api/extensions/{id}` - Get extension
- ✅ `PUT /api/extensions/{id}` - Update extension
- ✅ `PUT /api/extensions/{id}/number` - Update number
- ✅ `GET /api/users` - List users
- ✅ `GET /api/sites` - List sites
- ✅ `POST /api/sites` - Create site

### v2.0 New Endpoints
- 🆕 `POST /api/webhooks/subscriptions` - Webhook management
- 🆕 `GET /api/webhooks/subscriptions` - List subscriptions
- 🆕 `POST /api/webhooks/events` - Receive events
- 🆕 `POST /api/call-queues` - Call queue CRUD
- 🆕 `GET /api/call-queues` - List queues
- 🆕 `GET /api/phone-numbers/available` - Search numbers
- 🆕 `GET /api/analytics/call-logs` - CDR retrieval
- 🆕 `GET /metrics` - Prometheus metrics

---

## 🛡️ Security Enhancements

- ✅ Webhook signature validation (HMAC-SHA256)
- ✅ Request ID tracking for audit trails
- ✅ Structured logging for compliance
- ✅ Circuit breaker prevents abuse
- ✅ Rate limit compliance
- ✅ Docker security best practices

---

## 🎯 Next Steps

### Recommended Actions
1. ✅ Deploy with Docker Compose
2. ✅ Configure webhook endpoints
3. ✅ Set up Grafana dashboards
4. ✅ Configure alerting rules
5. ✅ Test call queue provisioning
6. ✅ Review metrics in Prometheus

### Future Roadmap (v3.0)
- [ ] IVR flow builder
- [ ] Real-time call control APIs
- [ ] Video conferencing integration
- [ ] SMS/MMS messaging
- [ ] Fax automation
- [ ] Team messaging APIs
- [ ] AI-powered analytics

---

## 📞 Support

- **Documentation:** http://localhost:8000/docs
- **Issues:** https://github.com/cloudwarriors-ai/rc-gateway/issues
- **Email:** hello@cloudwarriors.ai

---

## 🏆 Credits

Built with ❤️ by [Cloud Warriors](https://cloudwarriors.ai)

**Technologies:**
- FastAPI 0.111.0
- Python 3.11+
- Prometheus + Grafana
- Redis
- Docker
- RingCentral Platform API

---

**Version:** 2.0.0  
**Release Date:** October 2025  
**Status:** Production Ready ✅
