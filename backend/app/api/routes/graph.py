from fastapi import APIRouter, Depends

from app.schemas.graph import GraphResponse
from app.services.graph_service import GraphService, get_graph_service

router = APIRouter()


@router.get("/all", response_model=GraphResponse)
def get_all_graph_data(graph_service: GraphService = Depends(get_graph_service)) -> GraphResponse:
    return graph_service.get_full_graph()
