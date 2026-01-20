from enum import Enum
from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class RoomType(str, Enum):
    LIVING_ROOM = "living_room"
    KITCHEN = "kitchen"
    BEDROOM = "bedroom"
    BATHROOM = "bathroom"
    DINING_ROOM = "dining_room"
    OFFICE = "office"
    GARAGE = "garage"
    BALCONY = "balcony"
    CORRIDOR = "corridor"
    STORAGE = "storage"
    UTILITY = "utility"
    ENTRANCE = "entrance"
    OTHER = "other"

class AdjacencyType(str, Enum):
    DIRECT = "direct" # Connected by door or opening
    ADJACENT = "adjacent" # Share a wall, no direct access necessary
    NEAR = "near" # Close proximity
    FAR = "far" # Should be separated

class RoomConstraint(BaseModel):
    room_id: str
    min_area: Optional[float] = Field(None, description="Minimum area in square meters")
    max_area: Optional[float] = Field(None, description="Maximum area in square meters")
    aspect_ratio: Optional[float] = Field(None, description="Preferred width/height ratio")
    natural_light: bool = Field(False, description="Requires windows/natural light")

class Room(BaseModel):
    id: str = Field(..., description="Unique identifier for the room (e.g., 'living_room_1')")
    name: str = Field(..., description="Human readable name")
    type: RoomType
    description: Optional[str] = None
    constraints: RoomConstraint

class Adjacency(BaseModel):
    room_id_a: str
    room_id_b: str
    type: AdjacencyType
    description: Optional[str] = None

class GlobalConstraints(BaseModel):
    total_area_min: Optional[float] = None
    total_area_max: Optional[float] = None
    floors: int = Field(1, ge=1)
    style: Optional[str] = None
    site_width: Optional[float] = None
    site_depth: Optional[float] = None

class ArchitecturalProgram(BaseModel):
    rooms: List[Room]
    adjacencies: List[Adjacency]
    global_constraints: GlobalConstraints
    raw_prompt: Optional[str] = None
