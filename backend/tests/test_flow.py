import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

# Explicitly load .env file
env_path = backend_dir / ".env"
load_dotenv(env_path)

from app.core.llm import llm_parser
from app.core.graph import graph_builder
from app.schemas.architecture import ArchitecturalProgram

async def test_prompt_to_graph_flow():
    print("Starting Prompt -> Graph Flow Test")
    
    # 1. Simulate User Prompt
    user_prompt = "Design a modern 1-bedroom apartment with an open kitchen connected to the living room. The bedroom should have an en-suite bathroom. Total area around 60 sqm."
    print(f"\nUser Prompt: {user_prompt}")
    
    # 2. Parse Prompt (Mocking LLM for test stability if no key)
    print("\nParsing Prompt with LLM Service...")
    try:
        from app.config import settings
        # In a real test we might mock this, but here we want to see the service code run.
        # If no API key is set, the service might fail if we don't handle it.
        # For this script, let's manually construct the program if we can't call OpenAI
        if not settings.OPENAI_API_KEY:
            print("No OPENAI_API_KEY found. Using mock data for demonstration.")
            program = _get_mock_program(user_prompt)
        else:
            print("Using Real OpenAI API...")
            program = await llm_parser.parse_prompt(user_prompt)
            
        print("Prompt Parsed Successfully")
        print(f"   Rooms: {len(program.rooms)}")
        print(f"   Adjacencies: {len(program.adjacencies)}")
        print(f"   Global Constraints: {program.global_constraints}")
        
    except Exception as e:
        print(f"Parser Failed: {e}")
        return

    # 3. Build Constraint Graph
    print("\nBuilding Constraint Graph...")
    try:
        graph_data = graph_builder.build_constraint_graph(program)
        print("Graph Built Successfully")
        
        nodes = graph_data.get('nodes', [])
        # NetworkX 3.x node_link_data uses 'links' by default but can use 'edges'
        edges = graph_data.get('edges', graph_data.get('links', []))
        
        print(f"   Nodes: {len(nodes)}")
        print(f"   Edges: {len(edges)}")
        print(f"   Connected: {graph_data.get('graph', {}).get('is_connected')}")
        
    except Exception as e:
        print(f"Graph Builder Failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # 4. Generate Baseline Template
    print("\nGenerating Baseline Template...")
    try:
        from app.core.templates import template_service
        template = template_service.find_best_match(program)
        
        if template:
            print(f"Template Found: {template.name} ({template.id})")
            svg = template_service.render_svg(template)
            print(f"   SVG Generated ({len(svg)} chars)")
        else:
            print("No matching template found")
            
    except Exception as e:
        print(f"Template Generation Failed: {e}")
        return

    print("\nTest Completed Successfully")

def _get_mock_program(text: str) -> ArchitecturalProgram:
    from app.schemas.architecture import Room, RoomType, Adjacency, AdjacencyType, GlobalConstraints, RoomConstraint
    
    return ArchitecturalProgram(
        raw_prompt=text,
        rooms=[
            Room(id="living_1", name="Living Room", type=RoomType.LIVING_ROOM, constraints=RoomConstraint(room_id="living_1", min_area=20, natural_light=True)),
            Room(id="kitchen_1", name="Kitchen", type=RoomType.KITCHEN, constraints=RoomConstraint(room_id="kitchen_1", min_area=12, natural_light=True)),
            Room(id="bed_1", name="Bedroom", type=RoomType.BEDROOM, constraints=RoomConstraint(room_id="bed_1", min_area=15, natural_light=True)),
            Room(id="bath_1", name="Bathroom", type=RoomType.BATHROOM, constraints=RoomConstraint(room_id="bath_1", min_area=6, natural_light=False)),
        ],
        adjacencies=[
            Adjacency(room_id_a="living_1", room_id_b="kitchen_1", type=AdjacencyType.DIRECT),
            Adjacency(room_id_a="bed_1", room_id_b="bath_1", type=AdjacencyType.DIRECT),
            Adjacency(room_id_a="living_1", room_id_b="bed_1", type=AdjacencyType.NEAR),
        ],
        global_constraints=GlobalConstraints(total_area_min=55, total_area_max=65, floors=1)
    )

if __name__ == "__main__":
    asyncio.run(test_prompt_to_graph_flow())
