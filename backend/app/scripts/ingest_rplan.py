import asyncio
import os
import sys
import json
import random
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(backend_dir))

from app.database import AsyncSessionLocal
from app.models.project import Project
from app.models.prompt import Prompt
from app.models.layout import Layout, LayoutStatus

async def ingest_synthetic_rplan_data(limit: int = 100):
    """
    Simulates ingesting RPLAN data by creating synthetic records in the database.
    In a real scenario, this would read from the RPLAN dataset files.
    """
    print(f"🚀 Starting RPLAN Ingestion (Synthetic Mode) - Limit: {limit}")
    
    async with AsyncSessionLocal() as db:
        try:
            # Check if we have a default user
            # For this script we assume user ID 1 exists or we simulate it
            # In a real script we'd create a system user
            
            # Create synthetic data
            for i in range(limit):
                # 1. Simulate RPLAN Metadata
                rplan_id = f"rplan_{i}"
                num_rooms = random.randint(3, 8)
                area = random.randint(40, 150)
                
                # 2. Create Layout Record (Historical Data)
                # We store this as a 'completed' layout to serve as training data / reference
                
                # Note: In a real system, we might want to store these in a separate Dataset table,
                # but for this MVP we'll fit them into the Layouts model or just log them.
                # Here we will just print what we would do.
                
                layout_data = {
                    "source": "RPLAN",
                    "original_id": rplan_id,
                    "num_rooms": num_rooms,
                    "total_area": area,
                    "graph_embedding": [random.random() for _ in range(256)] # Simulated embedding
                }
                
                if i % 10 == 0:
                    print(f"Processed {i}/{limit} samples: {rplan_id}")

            print("✅ Ingestion Completed (Synthetic)")
            
        except Exception as e:
            print(f"❌ Ingestion Failed: {e}")

if __name__ == "__main__":
    asyncio.run(ingest_synthetic_rplan_data())
