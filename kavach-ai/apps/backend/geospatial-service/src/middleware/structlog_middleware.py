import structlog
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from structlog.contextvars import bind_contextvars, clear_contextvars
import time
import uuid

logger = structlog.get_logger()

class StructlogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        clear_contextvars()
        
        req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        corr_id = request.headers.get("X-Correlation-ID", req_id)
        
        bind_contextvars(
            request_id=req_id,
            correlation_id=corr_id,
            method=request.method,
            path=request.url.path
        )
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            logger.info("Request processed", 
                status_code=response.status_code, 
                latency=process_time
            )
            
            response.headers["X-Request-ID"] = req_id
            return response
            
        except Exception as exc:
            process_time = time.time() - start_time
            logger.error("Request failed", 
                exc_info=exc,
                latency=process_time
            )
            raise
