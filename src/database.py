import os
from config import DB_NAME
import asyncio, aiosqlite
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.getenv('DB_NAME')

class ItemManager:
    def __init__(self, table_name: str):
        self.table_name = table_name

    async def add(self, user_id: int, item: str):
        async with aiosqlite.connect(DB_NAME) as db:
            await db.execute("PRAGMA foreign_keys = ON")
            await db.execute(
                f"INSERT OR IGNORE INTO users (user_id) VALUES (?)",
                (user_id,)
            )
            await db.execute(
                f"INSERT INTO {self.table_name} (user_id, item) VALUES (?, ?)",
                (user_id, item)
            )
            await db.commit()

    async def get_all(self, user_id: int):
        async with aiosqlite.connect(DB_NAME) as db:
            cursor = await db.execute(
                f"SELECT item FROM {self.table_name} WHERE user_id = ? ORDER BY created_at",
                (user_id,)
            )
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

    async def delete(self, user_id: int, position: int):
        # получим все id записей пользователя, удалим по позиции (1-based)
        async with aiosqlite.connect(DB_NAME) as db:
            cursor = await db.execute(
                f"SELECT id FROM {self.table_name} WHERE user_id = ? ORDER BY created_at",
                (user_id,)
            )
            ids = [row[0] for row in await cursor.fetchall()]
            if 1 <= position <= len(ids):
                await db.execute(
                    f"DELETE FROM {self.table_name} WHERE id = ?",
                    (ids[position-1],)
                )
                await db.commit()
                return True
            return False

    async def clear(self, user_id: int):
        async with aiosqlite.connect(DB_NAME) as db:
            await db.execute(
                f"DELETE FROM {self.table_name} WHERE user_id = ?",
                (user_id,)
            )
            await db.commit()

#manager_table

tasks_manager = ItemManager("tasks")
magnit_manager = ItemManager("magnit")



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

async def create_magnit_task(db):
    await db.execute('''
        CREATE TABLE IF NOT EXISTS magnit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            link TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    ''')

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("PRAGMA foreign_keys = ON")
        await create_table_users(db)
        await create_table_task(db)
        await create_magnit_task(db)
        await db.commit()
    
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
    




# async def add_task(user_id: int, task: str):
#     """Добавляет задачу для пользователя"""
#     async with aiosqlite.connect(DB_NAME) as db:
#         await db.execute("PRAGMA foreign_keys = ON")
#         await db.execute(
#             "INSERT OR IGNORE INTO users (user_id, timer) VALUES (?, ?)",
#             (user_id, 0)
#         )
#         await db.execute(
#             "INSERT INTO tasks (user_id, task) VALUES (?, ?)",
#             (user_id, task)
#         )
#         await db.commit()

# async def add_magnit(user_id: int, task: str):
#     async with aiosqlite.connect(DB_NAME) as db:
#         await db.execute("PRAGMA foreign_keys = ON")
#         await db.execute(
#             "INSERT OR IGNORE INTO users (user_id, timer) VALUES (?, ?)",
#             (user_id, 0)
#         )
#         await db.execute(
#             "INSERT INTO magnit (user_id, link) VALUES (?, ?)",
#             (user_id, task)
#         )
#         await db.commit()

# async def delete_task(user_id: int, number: int):
#     async with aiosqlite.connect(DB_NAME) as db:
#         res = True
#         await db.execute("PRAGMA foreign_keys = ON")
#         cursor = await db.execute(
#         "SELECT id FROM tasks WHERE user_id = ? ORDER BY created_at",
#         (user_id,)
#         )
#         rows = await cursor.fetchall()
#         if number >= 1 and number <= len(rows):
#             task_id = rows[number - 1][0]
#             await db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
#             await db.commit()
#             print(f'Задача c номером {task_id} удалена')
#         else:
#             res = False
#         return res

# async def clear_task(user_id: int):
#     async with aiosqlite.connect(DB_NAME) as db:
#         await db.execute("PRAGMA foreign_keys = ON")
#         await db.execute(
#             "DELETE FROM tasks WHERE user_id = ?",
#             (user_id,)
#         )
#         await db.commit()

# async def get_tasks(user_id: int):
#     """Возвращает список задач пользователя"""
#     async with aiosqlite.connect(DB_NAME) as db:
#         await db.execute("PRAGMA foreign_keys = ON")
#         cursor = await db.execute(
#             "SELECT task FROM tasks WHERE user_id = ? ORDER BY created_at",
#             (user_id,)
#         )
#         rows = await cursor.fetchall()
#         return [row[0] for row in rows]
    
# async def get_links(user_id: int):
#     """Возвращает список задач пользователя"""
#     async with aiosqlite.connect(DB_NAME) as db:
#         await db.execute("PRAGMA foreign_keys = ON")
#         cursor = await db.execute(
#             "SELECT task FROM magnit WHERE user_id = ? ORDER BY created_at",
#             (user_id,)
#         )
#         rows = await cursor.fetchall()
#         return [row[0] for row in rows]