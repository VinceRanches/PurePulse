from fastapi import FastAPI

app = FastAPI(
    title="PurePulse",
    description="Model Service API Documentation",
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

@app.get('/health')
def health_check():
    return {'status': 'ok'}
