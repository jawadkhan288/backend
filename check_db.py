import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy import text
from database import engine

load_dotenv()

async def check_db():
    print("Checking profiles columns...")
    async with engine.connect() as conn:
        # Check columns of profiles table
        result = await conn.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'profiles';
        """))
        columns = result.fetchall()
        print("Profiles columns:", columns)

        # Alter profiles table to add phone, location, job_title, bio, avatar if they don't exist
        print("Altering profiles table if necessary...")
        await conn.execute(text("""
            ALTER TABLE public.profiles 
            ADD COLUMN IF NOT EXISTS phone text,
            ADD COLUMN IF NOT EXISTS location text,
            ADD COLUMN IF NOT EXISTS job_title text,
            ADD COLUMN IF NOT EXISTS bio text,
            ADD COLUMN IF NOT EXISTS avatar text;
        """))
        await conn.commit()
        print("Alter complete!")

        # Verify again
        result = await conn.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'profiles';
        """))
        columns = result.fetchall()
        print("Profiles columns after alter:", columns)

if __name__ == "__main__":
    asyncio.run(check_db())
