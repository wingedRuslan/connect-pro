from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from connect_pro.api.endpoints import router as api_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title="LinkedIn Profile Analyzer API",
        description="API for analyzing LinkedIn profiles",
        version="1.0.0"
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routes
    app.include_router(api_router, prefix="/api")
    
    return app

# Create the FastAPI application instance
app = create_app()


if __name__ == "__main__":
    """
    Run the application with uvicorn when script is executed directly.
    
    Use in development:
        python -m connect_pro.app
    
    Use in production:
        uvicorn connect_pro.app:app --host 0.0.0.0 --port 8000
    """
    import uvicorn
    
    uvicorn.run(
        "connect_pro.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Enable auto-reload during development
    )

