import asyncio
import os
import asyncpg
from pathlib import Path

async def run_migration():
    """Apply migration.sql to the database."""
    env_path = Path("backend/.env")
    if not env_path.exists():
        print("Error: .env not found")
        return

    with open(env_path, "r") as f:
        env_content = f.read()
    
    db_url = None
    for line in env_content.splitlines():
        if line.startswith("DATABASE_URL="):
            db_url = line.split("=", 1)[1]
            break
    
    if not db_url:
        print("Error: DATABASE_URL not found in .env")
        return

    migration_path = Path("backend/migration.sql")
    if not migration_path.exists():
        print("Error: migration.sql not found")
        return

    with open(migration_path, "r") as f:
        sql = f.read()

    print(f"Connecting to database...")
    conn = await asyncpg.connect(db_url)
    try:
        print("Executing migration...")
        await conn.execute(sql)
        print("Migration successful!")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(run_migration())
