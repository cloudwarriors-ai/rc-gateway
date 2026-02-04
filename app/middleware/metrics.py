import time
from typing import Callable

from fastapi import Request, Response
from prometheus_client import Counter, Histogram, Gauge
from starlette.middleware.base import BaseHTTPMiddleware

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"]
)

REQUESTS_IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "Number of HTTP requests in progress",
    ["method", "endpoint"]
)

RC_API_CALLS = Counter(
    "ringcentral_api_calls_total",
    "Total RingCentral API calls",
    ["endpoint", "status"]
)

RC_API_DURATION = Histogram(
    "ringcentral_api_duration_seconds",
    "RingCentral API call duration in seconds",
    ["endpoint"]
)

CIRCUIT_BREAKER_STATE = Gauge(
    "circuit_breaker_failures",
    "Current circuit breaker failure count"
)

RATE_LIMIT_HITS = Counter(
    "rate_limit_hits_total",
    "Total rate limit hits"
)


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        method = request.method
        path = request.url.path
        
        REQUESTS_IN_PROGRESS.labels(method=method, endpoint=path).inc()
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            
            REQUEST_COUNT.labels(
                method=method, 
                endpoint=path, 
                status=response.status_code
            ).inc()
            
            REQUEST_DURATION.labels(
                method=method, 
                endpoint=path
            ).observe(duration)
            
            return response
            
        finally:
            REQUESTS_IN_PROGRESS.labels(method=method, endpoint=path).dec()
