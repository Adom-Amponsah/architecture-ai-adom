from fastapi import APIRouter, Depends, HTTPException
from typing import Any, Dict, Optional
import base64
from pydantic import BaseModel

from app.api import deps
from app.models.user import User
from app.schemas.architecture import ArchitecturalProgram
from app.core.templates import template_service, LayoutTemplate
from app.core.graph import graph_builder
from app.services.ml_inference import ml_service
from app.services.geometry import geometry_service

router = APIRouter()

class GenerationResponse(BaseModel):
    template_id: str
    template_name: str
    svg_content: str
    glb_content: Optional[str] = None # Base64 encoded GLB file
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

@router.post("/diffusion", response_model=GenerationResponse)
async def generate_diffusion_layout(
    program: ArchitecturalProgram,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Generate a layout using the Generative Diffusion Model (AI) + 3D Extrusion.
    """
    try:
        # 1. Build Graph
        graph_data = graph_builder.build_constraint_graph(program)
        
        # 2. Run Inference (SVG + Geometry Data)
        # This will load models on first request if not loaded
        layout_result = ml_service.generate_layout(graph_data)
        
        svg_content = layout_result["svg"]
        geometry_data = layout_result["geometry"]
        
        # 3. Generate 3D Model (GLB)
        glb_bytes = geometry_service.create_3d_model(geometry_data)
        glb_b64 = base64.b64encode(glb_bytes).decode('utf-8')
        
        return GenerationResponse(
            template_id="ai_generated_v1",
            template_name="AI Diffusion Generation",
            svg_content=svg_content,
            glb_content=glb_b64,
            metadata={
                "score": 0.0, 
                "method": "diffusion_model_3d"
            }
        )
    except Exception as e:
        print(f"Diffusion Generation error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"AI Generation failed: {str(e)}")
