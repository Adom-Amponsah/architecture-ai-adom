from fastapi import APIRouter
from app.api.v1.endpoints import login, users, parser, graph, generation

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(parser.router, prefix="/parser", tags=["parser"])
api_router.include_router(graph.router, prefix="/graph", tags=["graph"])
api_router.include_router(generation.router, prefix="/generation", tags=["generation"])
