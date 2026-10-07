from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .api.routes import router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="The Autonomous Connected Intelligence Engine for Codebases"
)

# Enable CORS for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME} API v{settings.VERSION}",
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
