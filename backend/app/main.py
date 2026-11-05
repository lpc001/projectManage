from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.auth import router as auth_router
from app.api.routes.projects import router as projects_router
from app.api.routes.system import router as system_router
from app.core.config import get_settings


settings = get_settings()
app = FastAPI(title="大数据项目管理平台 API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router, prefix="/api")
app.include_router(projects_router, prefix="/api")
app.include_router(system_router, prefix="/api")


@app.get("/health", tags=["系统"])
def health() -> dict[str, str]:
    return {"status": "ok"}

