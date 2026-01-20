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
        You are an expert architectural assistant. Your goal is to convert user requests into a strict architectural program.
        Analyze the user's request and extract:
        1. A list of rooms with their types and specific constraints (area, light, etc.).
        2. Adjacency requirements between rooms.
        3. Global constraints for the building.

        If specific details (like area) are not mentioned, infer reasonable defaults based on standard architectural standards for residential buildings.
        Ensure every room has a unique ID.
        
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
                model="gpt-4-turbo-preview",
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
