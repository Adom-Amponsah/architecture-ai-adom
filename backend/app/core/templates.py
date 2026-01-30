from typing import List, Dict, Optional
from pydantic import BaseModel
from app.schemas.architecture import RoomType, ArchitecturalProgram

class TemplateRoom(BaseModel):
    id: str
    type: RoomType
    x: float
    y: float
    width: float
    height: float
    color: str = "#ffffff"

class LayoutTemplate(BaseModel):
    id: str
    name: str
    description: str
    rooms: List[TemplateRoom]
    width: float
    height: float
    
    def get_room_counts(self) -> Dict[RoomType, int]:
        counts = {}
        for room in self.rooms:
            counts[room.type] = counts.get(room.type, 0) + 1
        return counts

# Hardcoded MVP Templates
# In a real system, these would load from DB or JSON files
TEMPLATES = [
    LayoutTemplate(
        id="tpl_1bed_standard",
        name="Standard 1-Bedroom Apartment",
        description="A compact 1-bedroom unit with open living/kitchen area.",
        width=10.0,
        height=8.0,
        rooms=[
            TemplateRoom(id="living", type=RoomType.LIVING_ROOM, x=0, y=0, width=6, height=5, color="#FFE0B2"),
            TemplateRoom(id="kitchen", type=RoomType.KITCHEN, x=0, y=5, width=6, height=3, color="#FFCCBC"),
            TemplateRoom(id="bed", type=RoomType.BEDROOM, x=6, y=0, width=4, height=5, color="#BBDEFB"),
            TemplateRoom(id="bath", type=RoomType.BATHROOM, x=6, y=5, width=4, height=3, color="#CFD8DC"),
        ]
    ),
    LayoutTemplate(
        id="tpl_2bed_linear",
        name="Linear 2-Bedroom Layout",
        description="Efficient 2-bedroom layout arranged linearly.",
        width=14.0,
        height=7.0,
        rooms=[
            TemplateRoom(id="living", type=RoomType.LIVING_ROOM, x=4, y=0, width=5, height=7, color="#FFE0B2"),
            TemplateRoom(id="kitchen", type=RoomType.KITCHEN, x=0, y=0, width=4, height=4, color="#FFCCBC"),
            TemplateRoom(id="dining", type=RoomType.DINING_ROOM, x=0, y=4, width=4, height=3, color="#F0F4C3"),
            TemplateRoom(id="bed_master", type=RoomType.BEDROOM, x=9, y=0, width=5, height=4, color="#BBDEFB"),
            TemplateRoom(id="bed_guest", type=RoomType.BEDROOM, x=9, y=4, width=5, height=3, color="#E1BEE7"),
            TemplateRoom(id="bath", type=RoomType.BATHROOM, x=4, y=5, width=2, height=2, color="#CFD8DC"), # Small internal bath
        ]
    ),
    LayoutTemplate(
        id="tpl_3bed_family",
        name="Family 3-Bedroom Apartment",
        description="Spacious 3-bedroom unit suitable for families.",
        width=16.0,
        height=10.0,
        rooms=[
            TemplateRoom(id="living", type=RoomType.LIVING_ROOM, x=0, y=0, width=8, height=6, color="#FFE0B2"),
            TemplateRoom(id="dining", type=RoomType.DINING_ROOM, x=8, y=0, width=5, height=4, color="#F0F4C3"),
            TemplateRoom(id="kitchen", type=RoomType.KITCHEN, x=13, y=0, width=3, height=4, color="#FFCCBC"),
            TemplateRoom(id="corridor", type=RoomType.CORRIDOR, x=0, y=6, width=16, height=1, color="#E0E0E0"),
            TemplateRoom(id="bed_master", type=RoomType.BEDROOM, x=0, y=7, width=5, height=3, color="#BBDEFB"),
            TemplateRoom(id="bed_2", type=RoomType.BEDROOM, x=5, y=7, width=4, height=3, color="#E1BEE7"),
            TemplateRoom(id="bed_3", type=RoomType.BEDROOM, x=9, y=7, width=4, height=3, color="#E1BEE7"),
            TemplateRoom(id="bath_1", type=RoomType.BATHROOM, x=13, y=7, width=3, height=3, color="#CFD8DC"),
            TemplateRoom(id="bath_master", type=RoomType.BATHROOM, x=13, y=4, width=3, height=2, color="#CFD8DC"),
        ]
    ),
    LayoutTemplate(
        id="tpl_office_small",
        name="Small Office Suite",
        description="Workspace for a small team with meeting room.",
        width=12.0,
        height=8.0,
        rooms=[
            TemplateRoom(id="open_office", type=RoomType.LIVING_ROOM, x=0, y=0, width=8, height=8, color="#B3E5FC"), # Using Living as Open Office
            TemplateRoom(id="meeting", type=RoomType.OFFICE, x=8, y=0, width=4, height=5, color="#C5CAE9"),
            TemplateRoom(id="pantry", type=RoomType.KITCHEN, x=8, y=5, width=2, height=3, color="#FFCCBC"),
            TemplateRoom(id="restroom", type=RoomType.BATHROOM, x=10, y=5, width=2, height=3, color="#CFD8DC"),
        ]
    ),
    LayoutTemplate(
        id="tpl_studio",
        name="Compact Studio",
        description="Open plan studio apartment.",
        width=6.0,
        height=8.0,
        rooms=[
            TemplateRoom(id="main", type=RoomType.LIVING_ROOM, x=0, y=2, width=6, height=6, color="#FFE0B2"), # Combined living/sleeping
            TemplateRoom(id="kitchen", type=RoomType.KITCHEN, x=0, y=0, width=3, height=2, color="#FFCCBC"),
            TemplateRoom(id="bath", type=RoomType.BATHROOM, x=3, y=0, width=3, height=2, color="#CFD8DC"),
        ]
    )
]

class TemplateService:
    def find_best_match(self, program: ArchitecturalProgram) -> Optional[LayoutTemplate]:
        """
        Simple heuristic matching based on room types and counts.
        """
        required_counts = {}
        for room in program.rooms:
            required_counts[room.type] = required_counts.get(room.type, 0) + 1
            
        best_template = None
        max_score = -1
        
        for template in TEMPLATES:
            tpl_counts = template.get_room_counts()
            score = 0
            
            # Score based on matching room types present
            for r_type, count in required_counts.items():
                if r_type in tpl_counts:
                    # If template has enough of this room type
                    if tpl_counts[r_type] >= count:
                        score += 2
                    else:
                        score += 1 # Partial match
                else:
                    score -= 1 # Missing required room
            
            # Penalize for extra rooms in template that weren't asked for? 
            # Maybe not for MVP, users might like bonus rooms.
            
            if score > max_score:
                max_score = score
                best_template = template
                
        return best_template

    def render_svg(self, template: LayoutTemplate) -> str:
        """
        Generates a simple SVG representation of the template.
        """
        scale = 50 # pixels per meter
        width_px = template.width * scale
        height_px = template.height * scale
        
        svg_parts = [
            f'<svg width="{width_px}" height="{height_px}" viewBox="0 0 {width_px} {height_px}" xmlns="http://www.w3.org/2000/svg" style="background-color: #f5f5f5;">'
        ]
        
        # Draw rooms
        for room in template.rooms:
            x = room.x * scale
            y = room.y * scale
            w = room.width * scale
            h = room.height * scale
            
            rect = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{room.color}" stroke="#333" stroke-width="2" />'
            text_x = x + w/2
            text_y = y + h/2
            text = f'<text x="{text_x}" y="{text_y}" font-family="Arial" font-size="14" text-anchor="middle" fill="#333">{room.type.value.replace("_", " ").title()}</text>'
            
            svg_parts.append(rect)
            svg_parts.append(text)
            
        svg_parts.append('</svg>')
        return "\n".join(svg_parts)

template_service = TemplateService()
