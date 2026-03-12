import os
from config import DB_NAME
import asyncio, aiosqlite
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.getenv('DB_NAME')

async def create_table_users(db):
    await db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            timer INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

async def create_table_task(db):
    await db.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            task TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    ''')

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("PRAGMA foreign_keys = ON")
        await create_table_users(db)
        await create_table_task(db)
        await db.commit()


async def add_task(user_id: int, task: str):
    """Добавляет задачу для пользователя"""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("PRAGMA foreign_keys = ON")
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, timer) VALUES (?, ?)",
            (user_id, 0)
        )
        await db.execute(
            "INSERT INTO tasks (user_id, task) VALUES (?, ?)",
            (user_id, task)
        )
        await db.commit()

async def delete_task(user_id: int, number: int):
    async with aiosqlite.connect(DB_NAME) as db:
        res = True
        await db.execute("PRAGMA foreign_keys = ON")
        cursor = await db.execute(
        "SELECT id FROM tasks WHERE user_id = ? ORDER BY created_at",
        (user_id,)
        )
        rows = await cursor.fetchall()
        if number >= 1 and number <= len(rows):
            task_id = rows[number - 1][0]
            await db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            await db.commit()
            print(f'Задача c номером {task_id} удалена')
        else:
            res = False
        return res

async def clear_task(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("PRAGMA foreign_keys = ON")
        await db.execute(
            "DELETE FROM tasks WHERE user_id = ?",
            (user_id,)
        )
        await db.commit()

async def get_tasks(user_id: int):
    """Возвращает список задач пользователя"""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("PRAGMA foreign_keys = ON")
        cursor = await db.execute(
            "SELECT task FROM tasks WHERE user_id = ? ORDER BY created_at",
            (user_id,)
        )
        rows = await cursor.fetchall()
        return [row[0] for row in rows]
    
async def add_timer(user_id: int, number: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("PRAGMA foreign_keys = ON")
        await db.execute(
            "UPDATE users SET timer = ? where user_id = ?",
            (number, user_id)
        )
        await db.commit()

async def get_timer(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("PRAGMA foreign_keys = ON")
        cur = await db.execute(
            "SELECT timer FROM users WHERE user_id = (?)",
            (user_id,)
        )
        timer = await cur.fetchall()
        return timer[0]