import asyncio
import aiosqlite
from database import get_timer
from aiogram import Bot
from config import DB_NAME

async def reminder(bot: Bot):
    while True:
        #timer = get_timer()
        await asyncio.sleep(60)
        async with aiosqlite.connect(DB_NAME) as db:
            await db.execute("PRAGMA foreign_keys = ON")
            cursor = await db.execute("SELECT DISTINCT user_id FROM users")
            users = await cursor.fetchall()
            lst_users = [user[0] for user in users]
            

            for user_id in lst_users:
                cur = await db.execute(
                    "SELECT task FROM tasks WHERE user_id = ? ORDER BY created_at",
                    (user_id,)
                )
                tasks = await cur.fetchall()
                
                if tasks:
                    # Формируем текст напоминания
                    task_list = '\n'.join([f'{i + 1}. {item[0]}' for i, item in enumerate(tasks)])
                    text = f"Напоминание о задачах 🔔\n{task_list}"
                    
                    try:
                        await bot.send_message(chat_id=user_id, text=text)
                    except Exception as e:
                        # Пользователь мог заблокировать бота или другая ошибка
                        print(f"Не удалось отправить напоминание пользователю {user_id}: {e}")
                        # Опционально: удалить задачи этого пользователя
                        # await db.execute("DELETE FROM tasks WHERE user_id = ?", (user_id,))
                        # await db.commit()
                
                await asyncio.sleep(0.1)  # пауза между отправками   