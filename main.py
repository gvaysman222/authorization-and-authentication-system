from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.session import engine, SessionLocal
from app.db.base import Base
from app.api.routers import auth as auth_router
from app.api.routers import users as users_router
from app.api.routers import admin as admin_router
from app.api.routers import mock as mock_router
from app.services.seed import run_seed
from fastapi.openapi.utils import get_openapi

app = FastAPI(title="Custom Auth & RBAC")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS, allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Custom Auth & RBAC",
        version="1.0.0",
        routes=app.routes,
    )
    openapi_schema.setdefault("components", {})
    openapi_schema["components"].setdefault("securitySchemes", {})
    openapi_schema["components"]["securitySchemes"]["bearerAuth"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "OpaqueToken"
    }
    # По умолчанию показываем, что эндпоинты используют bearer (это только для UI)
    openapi_schema["security"] = [{"bearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        run_seed(db)

app.include_router(auth_router.router)
app.include_router(users_router.router)
app.include_router(admin_router.router)
app.include_router(mock_router.router)

@app.get("/")
def root():
    return {"service": "Custom Auth & RBAC", "status": "ok"}
