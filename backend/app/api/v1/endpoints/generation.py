from fastapi import APIRouter, Depends, HTTPException
from typing import Any, Dict
from pydantic import BaseModel

from app.api import deps
from app.models.user import User
from app.schemas.architecture import ArchitecturalProgram
from app.core.templates import template_service, LayoutTemplate

router = APIRouter()

class GenerationResponse(BaseModel):
    template_id: str
    template_name: str
    svg_content: str
    metadata: Dict[str, Any]

@router.post("/baseline", response_model=GenerationResponse)
async def generate_baseline_layout(
    program: ArchitecturalProgram,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Generate a baseline layout using deterministic template matching.
    This serves as a fallback or quick-start option before full AI generation.
    """
    try:
        # Find best matching template
        template = template_service.find_best_match(program)
        
        if not template:
            raise HTTPException(status_code=404, detail="No suitable template found for the given program constraints.")
            
        # Generate SVG visualization
        svg_output = template_service.render_svg(template)
        
        return GenerationResponse(
            template_id=template.id,
            template_name=template.name,
            svg_content=svg_output,
            metadata={
                "width": template.width,
                "height": template.height,
                "description": template.description
            }
        )
        
    except Exception as e:
        # If it's already an HTTPException, re-raise it
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")
