from fastapi import APIRouter, Depends, HTTPException
from typing import Any, Dict
from pydantic import BaseModel

from app.api import deps
from app.models.user import User
from app.schemas.architecture import ArchitecturalProgram
from app.core.graph import graph_builder

router = APIRouter()

class GraphResponse(BaseModel):
    graph_data: Dict[str, Any]
    stats: Dict[str, Any]

@router.post("/build", response_model=GraphResponse)
async def build_graph(
    program: ArchitecturalProgram,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Convert an Architectural Program into a Constraint Graph.
    """
    try:
        graph_data = graph_builder.build_constraint_graph(program)
        
        # Extract some basic stats
        node_count = len(graph_data.get('nodes', []))
        edge_count = len(graph_data.get('edges', graph_data.get('links', [])))
        
        return {
            "graph_data": graph_data,
            "stats": {
                "node_count": node_count,
                "edge_count": edge_count,
                "is_connected": graph_data.get("graph", {}).get("is_connected", False)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph construction failed: {str(e)}")
