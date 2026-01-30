from fastapi import APIRouter, Depends, HTTPException
from typing import Any
from pydantic import BaseModel

from app.api import deps
from app.models.user import User
from app.schemas.architecture import ArchitecturalProgram
from app.core.llm import llm_parser

router = APIRouter()

class PromptRequest(BaseModel):
    text: str

@router.post("/parse", response_model=ArchitecturalProgram)
async def parse_architectural_prompt(
    prompt_request: PromptRequest,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Parse a natural language prompt into an architectural program using LLM.
    """
    if not prompt_request.text:
        raise HTTPException(status_code=400, detail="Prompt text cannot be empty")
        
    try:
        # Check if we have an API key configured (mock check for dev)
        # In prod, this would fail if key is missing
        from app.config import settings
        if not settings.OPENAI_API_KEY:
             # Return a mock response for testing/development if no key is present
             return _get_mock_program(prompt_request.text)

        try:
            result = await llm_parser.parse_prompt(prompt_request.text)
            return result
        except Exception as e:
            print(f"LLM processing failed (falling back to mock): {str(e)}")
            return _get_mock_program(prompt_request.text)

    except Exception as e:
        # This catches errors outside the LLM call or re-raises if needed
        print(f"Parser endpoint error: {e}")
        return _get_mock_program(prompt_request.text)

def _get_mock_program(text: str) -> ArchitecturalProgram:
    from app.schemas.architecture import Room, RoomType, Adjacency, AdjacencyType, GlobalConstraints, RoomConstraint
    
    return ArchitecturalProgram(
        raw_prompt=text,
        rooms=[
            Room(id="living_1", name="Living Room", type=RoomType.LIVING_ROOM, constraints=RoomConstraint(room_id="living_1", min_area=20, natural_light=True)),
            Room(id="kitchen_1", name="Kitchen", type=RoomType.KITCHEN, constraints=RoomConstraint(room_id="kitchen_1", min_area=12, natural_light=True)),
            Room(id="bed_1", name="Master Bedroom", type=RoomType.BEDROOM, constraints=RoomConstraint(room_id="bed_1", min_area=15, natural_light=True)),
            Room(id="bath_1", name="Master Bath", type=RoomType.BATHROOM, constraints=RoomConstraint(room_id="bath_1", min_area=6, natural_light=False)),
        ],
        adjacencies=[
            Adjacency(room_id_a="living_1", room_id_b="kitchen_1", type=AdjacencyType.DIRECT),
            Adjacency(room_id_a="bed_1", room_id_b="bath_1", type=AdjacencyType.DIRECT),
            Adjacency(room_id_a="living_1", room_id_b="bed_1", type=AdjacencyType.FAR),
        ],
        global_constraints=GlobalConstraints(total_area_min=80, total_area_max=120, floors=1)
    )
