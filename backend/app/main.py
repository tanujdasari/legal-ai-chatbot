
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes.chat import router as chat_router
from app.api.routes.documents import router as documents_router
from app.api.routes.history import router as history_router

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Legal AI Assistant for US and Indian laws",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"],
)

# Register API routers
app.include_router(chat_router)
app.include_router(documents_router)
app.include_router(history_router)


@app.get("/")
def home():
    return {
        "message": "Welcome to Legal AI Assistant",
        "status": "running",
        "jurisdictions": ["United States", "India"],
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
