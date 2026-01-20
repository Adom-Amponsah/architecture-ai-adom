import asyncio
import logging
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from app.database import AsyncSessionLocal
from app.models.user import User
from app.core.security import get_password_hash
from sqlalchemy import select

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_initial_data() -> None:
    async with AsyncSessionLocal() as session:
        try:
            logger.info("Creating initial data")
            
            # Check if user exists
            result = await session.execute(select(User).filter(User.email == "admin@example.com"))
            user = result.scalars().first()
            
            if not user:
                user = User(
                    email="admin@example.com",
                    hashed_password=get_password_hash("password"),
                    full_name="Admin User",
                    is_superuser=True,
                    is_active=True,
                )
                session.add(user)
                await session.commit()
                logger.info("Superuser created")
            else:
                logger.info("Superuser already exists")
                
        except Exception as e:
            logger.error(f"Error creating initial data: {e}")
            raise

if __name__ == "__main__":
    asyncio.run(create_initial_data())
