from fastapi import APIRouter

from app.api.routes import admin, auth, graph, learning, notifications, recommend, teacher

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(graph.router, prefix="/graph", tags=["graph"])
api_router.include_router(learning.router, prefix="/learning", tags=["learning"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(recommend.router, prefix="/recommend", tags=["recommend"])
api_router.include_router(teacher.router, prefix="/teacher", tags=["teacher"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
