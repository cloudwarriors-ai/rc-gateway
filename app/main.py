import logging
from fastapi import FastAPI

from app.api.routes import router as api_router
from app.api.enhanced_routes import router as enhanced_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="RingCentral Call Center Gateway",
        description="Production-ready FastAPI service for RingCentral telephony automation with comprehensive management features",
        version="3.0.0"
    )
    
    app.include_router(api_router, prefix="/api")
    app.include_router(enhanced_router, prefix="/api")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    return app


app = create_app()
