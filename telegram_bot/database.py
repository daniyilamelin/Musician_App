import asyncpg
import os

async def find_id(telegram_id: int, user_id: int):
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"))
    await conn.execute("""
        UPDATE main_user 
        SET telegram_id = $1, is_verified = True
        WHERE id = $2;
    """, telegram_id, user_id)
    await conn.close()