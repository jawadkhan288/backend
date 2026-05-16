"""
migrate.py — Creates all database tables in Supabase PostgreSQL.
Run once after setting up your .env file:
    python migrate.py
"""
import asyncio
from database import engine, Base

# Import models so SQLAlchemy registers them
import models  # noqa: F401


async def create_tables():
    print("🔧 Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tables created successfully!")
    print("   → users")
    print("   → candidates")


if __name__ == "__main__":
    asyncio.run(create_tables())
