import sys
import os
from pathlib import Path
from fastapi.testclient import TestClient
from dotenv import load_dotenv

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

# Explicitly load .env file
env_path = backend_dir / ".env"
load_dotenv(env_path)

# Mock Env Vars if needed (though we want to test with real loaded models if possible)
# os.environ["MOCK_AUTH"] = "true" 

from app.main import app
from app.schemas.architecture import ArchitecturalProgram

client = TestClient(app)

def test_diffusion_generation():
    print("Testing Diffusion Generation Endpoint...")
    
    # Mock Program
    program_data = {
        "raw_prompt": "A test apartment",
        "rooms": [
            {"id": "r1", "name": "Living Room", "type": "living_room", "constraints": {"room_id": "r1", "min_area": 20, "natural_light": True}},
            {"id": "r2", "name": "Kitchen", "type": "kitchen", "constraints": {"room_id": "r2", "min_area": 10, "natural_light": True}},
            {"id": "r3", "name": "Bedroom", "type": "bedroom", "constraints": {"room_id": "r3", "min_area": 15, "natural_light": True}}
        ],
        "adjacencies": [
            {"room_id_a": "r1", "room_id_b": "r2", "type": "direct", "description": "connected"}
        ],
        "global_constraints": {
            "total_area_min": 50,
            "total_area_max": 70,
            "floors": 1
        }
    }
    
    # Needs auth? The endpoint depends on get_current_active_user.
    # If MOCK_AUTH is true in .env (which it is), we should be good.
    
    response = client.post(
        "/api/v1/generation/diffusion",
        json=program_data
    )
    
    if response.status_code != 200:
        print(f"Failed: {response.status_code}")
        print(response.text)
    else:
        data = response.json()
        print("Success!")
        print(f"Template Name: {data['template_name']}")
        print(f"SVG Length: {len(data['svg_content'])}")
        if data.get('glb_content'):
             print(f"GLB Length: {len(data['glb_content'])} (Base64)")
        print(f"Metadata: {data['metadata']}")
        assert "svg" in data['svg_content']
        assert data['glb_content'] is not None

if __name__ == "__main__":
    test_diffusion_generation()
