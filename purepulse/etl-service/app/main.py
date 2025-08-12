from fastapi import FastAPI

from app.routes.purpleair import router as purpleair_router
from app.routes.wunderground import router as wunderground_router

app = FastAPI(
    title="PurePulse",
    description="ETL Service API Documentation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    swagger_ui_parameters={
        "tryItOutEnabled": True,
        "displayRequestDuration": True,
        "defaultModelsExpandDepth": 1,
        "defaultModelExpandDepth": 1
    }
)

# Include routers
app.include_router(router=purpleair_router, tags=["Extraction"])
app.include_router(router=wunderground_router, tags=["Extraction"])

@app.get('/health')
def health_check():
    return {'status': 'ok'}
