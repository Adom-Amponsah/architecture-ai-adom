import json
from typing import Any, Dict
import openai
from app.config import settings
from app.schemas.architecture import ArchitecturalProgram

class LLMParserService:
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def parse_prompt(self, user_prompt: str) -> ArchitecturalProgram:
        """
        Parses a natural language architectural prompt into a structured program using OpenAI API directly.
        """
        system_prompt = """
        You are a senior architectural program analyst. Convert user requests into a strict architectural program JSON.
        Treat the user's text as requirements for real buildings. Be precise, deterministic, and complete.

        HARD RULES
        1) Extract EVERY room explicitly mentioned (bedrooms, bathrooms, dining room, balcony, office, etc.).
        2) Convert counts into distinct rooms ("2-bedroom" => bedroom_1 + bedroom_2).
        3) Do NOT invent rooms that are not implied by the prompt.
        4) Ensure every room has a unique id and constraints.room_id set to that id.
        5) Output JSON only (no commentary, no markdown), matching the schema below.

        NORMALIZATION RULES
        - Use only these types:
          living_room, kitchen, bedroom, bathroom, dining_room, office, garage,
          balcony, corridor, storage, utility, entrance, other
        - Map synonyms:
          master bedroom -> bedroom
          ensuite -> bathroom
          wc / toilet / powder room -> bathroom
          open kitchen -> kitchen
          living area / lounge -> living_room
          study -> office
        - If a room name implies a count (e.g., "two bathrooms"), create separate rooms with distinct ids.

        ADJACENCY RULES
        - "open kitchen" or "open plan" => kitchen adjacent to living_room (type: direct)
        - dining_room mentioned => dining_room adjacent to kitchen (type: near unless explicit)
        - balcony mentioned => balcony adjacent to living_room (type: adjacent unless explicit)
        - ensuite mentioned => that bathroom adjacent to the associated bedroom (type: direct)
        - If explicit adjacency terms appear ("next to", "adjacent", "connected"), use type direct/adjacent as appropriate.

        DEFAULTS
        - If area is unspecified, infer reasonable min/max areas for residential rooms.
        - If floors not specified, set floors = 1.
        - If style not specified, leave style as "".

        EXAMPLE BEHAVIOR (informative only):
        "Design a 3-bedroom family apartment with two bathrooms and a dining room"
        => bedrooms: 3 rooms, bathrooms: 2 rooms, dining_room: 1 room

        Output must be a valid JSON object matching the following structure:
        {
            "rooms": [
                {
                    "id": "string",
                    "name": "string",
                    "type": "living_room|kitchen|bedroom|bathroom|dining_room|office|garage|balcony|corridor|storage|utility|entrance|other",
                    "description": "string",
                    "constraints": {
                        "room_id": "string",
                        "min_area": float,
                        "max_area": float,
                        "aspect_ratio": float,
                        "natural_light": boolean
                    }
                }
            ],
            "adjacencies": [
                {
                    "room_id_a": "string",
                    "room_id_b": "string",
                    "type": "direct|adjacent|near|far",
                    "description": "string"
                }
            ],
            "global_constraints": {
                "total_area_min": float,
                "total_area_max": float,
                "floors": int,
                "style": "string",
                "site_width": float,
                "site_depth": float
            }
        }
        """

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0
            )
            
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from LLM")
                
            data = json.loads(content)
            
            # Post-process to ensure data consistency
            if "rooms" in data:
                for room in data["rooms"]:
                    # Ensure constraints have room_id matching the room
                    if "constraints" in room:
                        if "room_id" not in room["constraints"]:
                            room["constraints"]["room_id"] = room.get("id")
            
            program = ArchitecturalProgram(
                raw_prompt=user_prompt,
                **data
            )
            return program

        except Exception as e:
            print(f"Error parsing LLM response: {e}")
            raise e

llm_parser = LLMParserService()
