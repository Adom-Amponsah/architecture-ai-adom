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
        
        # Generate 3D Model (GLB) from Template Rooms
        # Convert template rooms to geometry format
        geometry_data = []
        scale = 50 # matches SVG scale
        for room in template.rooms:
            # Template x,y are in meters (or units), we need to scale if we want to match SVG coordinates
            # But geometry service takes "pixels" and scales them down by 0.02 to get meters.
            # So if we want 1 unit in template to be 1 meter in 3D:
            # geometry service: w * 0.02 = meters. => w_pixels = meters / 0.02 = meters * 50.
            # So passing (meters * 50) as pixels works perfectly with the current geometry service logic.
            
            w_px = room.width * scale
            h_px = room.height * scale
            x_px = room.x * scale
            y_px = room.y * scale
            
            geometry_data.append({
                "id": room.id,
                "name": room.type.value.replace("_", " ").title(),
                "type": room.type,
                "x": x_px,
                "y": y_px,
                "width": w_px,
                "height": h_px,
                "center_x": x_px + w_px/2,
                "center_y": y_px + h_px/2
            })
            
        glb_bytes = geometry_service.create_3d_model(geometry_data)
        glb_b64 = None
        if glb_bytes:
            glb_b64 = base64.b64encode(glb_bytes).decode('utf-8')
        
        return GenerationResponse(
            template_id=template.id,
            template_name=template.name,
            svg_content=svg_output,
            glb_content=glb_b64,
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
        try:
            # This will load models on first request if not loaded
            layout_result = ml_service.generate_layout(graph_data)
        except RuntimeError as ml_err:
            print(f"ML Service unavailable: {ml_err}. Falling back to mock generation.")
            # Fallback to a deterministic mock result if ML is missing
            from app.core.templates import template_service
            # Use a template but pretend it's AI generated for the flow
            template = template_service.find_best_match(program)
            if not template: 
                 raise HTTPException(status_code=404, detail="Generation failed and no fallback template found.")
            
            # Convert template to geometry format expected by 3D service
            # We need to parse the SVG or just mock the geometry data for the template
            # For simplicity, let's just use the template's SVG and generate some dummy 3D boxes based on rooms
            
            # Quick mock geometry from rooms
            mock_geometry = []
            import random
            x_offset, y_offset = 0, 0
            for room in program.rooms:
                w, h = 150, 150 # Mock size
                mock_geometry.append({
                    "id": room.id,
                    "name": room.name,
                    "type": room.type,
                    "x": x_offset,
                    "y": y_offset,
                    "width": w,
                    "height": h,
                    "center_x": x_offset + w/2,
                    "center_y": y_offset + h/2
                })
                x_offset += 160
                if x_offset > 300:
                    x_offset = 0
                    y_offset += 160
            
            layout_result = {
                "svg": template_service.render_svg(template),
                "geometry": mock_geometry
            }

        svg_content = layout_result["svg"]
        geometry_data = layout_result["geometry"]
        
        # 3. Generate 3D Model (GLB)
        glb_bytes = geometry_service.create_3d_model(geometry_data)
        glb_b64 = None
        if glb_bytes:
            glb_b64 = base64.b64encode(glb_bytes).decode('utf-8')
        
        return GenerationResponse(
            template_id="ai_generated_mock" if "mock_geometry" in locals() else "ai_generated_v1",
            template_name="AI Diffusion Generation (Mock)" if "mock_geometry" in locals() else "AI Diffusion Generation",
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
