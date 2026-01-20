import sys
import os
from pathlib import Path

# Set mock env vars for testing BEFORE importing app
os.environ["DATABASE_URL"] = "postgresql://postgres:password@localhost:5432/architecture_ai_test"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["MINIO_ENDPOINT"] = "localhost:9000"
os.environ["MINIO_ACCESS_KEY"] = "minioadmin"
os.environ["MINIO_SECRET_KEY"] = "minioadmin"
os.environ["OPENAI_API_KEY"] = "sk-test-key"

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from fastapi.testclient import TestClient
from app.main import app
from app.core.templates import template_service

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_parse_prompt_mock():
    # We need to mock the authentication dependency since we don't have a running DB with users
    # For this test, we can override the dependency
    from app.api.deps import get_current_active_user
    from app.models.user import User
    
    async def mock_get_current_active_user():
        return User(id=1, email="test@example.com", is_active=True)
    
    app.dependency_overrides[get_current_active_user] = mock_get_current_active_user
    
    # Mock the LLM service to avoid API calls/keys
    from app.core.llm import llm_parser
    from app.schemas.architecture import ArchitecturalProgram, Room, RoomType, Adjacency, GlobalConstraints, RoomConstraint
    
    async def mock_parse_prompt(text: str):
        return ArchitecturalProgram(
            raw_prompt=text,
            rooms=[
                Room(id="room1", name="Living", type=RoomType.LIVING_ROOM, constraints=RoomConstraint(room_id="room1", min_area=20, natural_light=True))
            ],
            adjacencies=[],
            global_constraints=GlobalConstraints(floors=1)
        )
    
    original_parse = llm_parser.parse_prompt
    llm_parser.parse_prompt = mock_parse_prompt
    
    # Mock settings to force using the parser service instead of internal mock
    from app.config import settings
    original_api_key = settings.OPENAI_API_KEY
    settings.OPENAI_API_KEY = "sk-fake-key-for-test"
    
    try:
        response = client.post(
            "/api/v1/parser/parse",
            json={"text": "design a living room"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["rooms"]) == 1
        assert data["rooms"][0]["type"] == "living_room"
        
    finally:
        # Restore original method and overrides
        llm_parser.parse_prompt = original_parse
        settings.OPENAI_API_KEY = original_api_key
        app.dependency_overrides = {}

def test_generate_baseline():
    # Mock auth
    from app.api.deps import get_current_active_user
    from app.models.user import User
    
    async def mock_get_current_active_user():
        return User(id=1, email="test@example.com", is_active=True)
    
    app.dependency_overrides[get_current_active_user] = mock_get_current_active_user
    
    # Construct a valid program payload
    program_data = {
        "rooms": [
            {"id": "l1", "name": "Living", "type": "living_room", "constraints": {"room_id": "l1", "min_area": 20, "natural_light": True}},
            {"id": "k1", "name": "Kitchen", "type": "kitchen", "constraints": {"room_id": "k1", "min_area": 10, "natural_light": True}},
            {"id": "b1", "name": "Bed", "type": "bedroom", "constraints": {"room_id": "b1", "min_area": 15, "natural_light": True}},
            {"id": "ba1", "name": "Bath", "type": "bathroom", "constraints": {"room_id": "ba1", "min_area": 5, "natural_light": False}}
        ],
        "adjacencies": [],
        "global_constraints": {"floors": 1},
        "raw_prompt": "test prompt"
    }
    
    response = client.post(
        "/api/v1/generation/baseline",
        json=program_data
    )
    
    if response.status_code != 200:
        print(f"Generate baseline failed: {response.status_code}")
        print(response.text)

    # Should find the 1-bedroom template
    assert response.status_code == 200
    data = response.json()
    assert "svg_content" in data
    assert "template_name" in data
    assert "Standard 1-Bedroom" in data["template_name"]
    
    app.dependency_overrides = {}

if __name__ == "__main__":
    # Simple manual runner if pytest not available
    try:
        test_health_check()
        print("Health check passed")
        test_parse_prompt_mock()
        print("Parse prompt passed")
        test_generate_baseline()
        print("Generate baseline passed")
    except Exception as e:
        print(f"Tests failed: {e}")
        import traceback
        traceback.print_exc()
