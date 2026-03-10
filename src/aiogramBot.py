from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import BotCommand
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
import aiohttp
import asyncio, aiosqlite
from dotenv import load_dotenv
import os

load_dotenv()

class States(StatesGroup):
    task_state = State()
    delete_state = State()

DB_NAME = os.getenv('DB_NAME')
BOT_TOKEN = os.getenv('BOT_TOKEN')
CATS_URL = 'https://api.thecatapi.com/v1/images/search'

bot = Bot(BOT_TOKEN)
dp = Dispatcher()
tasks = {}

async def init_db():
    """Создаёт таблицу, если её нет"""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                task TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.commit()

async def add_task(user_id: int, task: str):
    """Добавляет задачу для пользователя"""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT INTO tasks (user_id, task) VALUES (?, ?)",
            (user_id, task)
        )
        await db.commit()

async def clear_task(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "DELETE FROM tasks WHERE user_id = ?",
            (user_id,)
        )
        await db.commit()

async def setup_commands():
    """Установка команд бота"""
    commands = [
        BotCommand(command="start", description="Информация"),
        BotCommand(command="add", description="Добавить задачу"),
        BotCommand(command="tasks", description="Список задач"),
        BotCommand(command="cat", description="Посмотреть на котика"),
        BotCommand(command="delete", description="Убрать задачу"),
        BotCommand(command="clear_task", description="Очистить все задачи"),
    ]
    try:
        await bot.set_my_commands(commands)
        print("Меню команд обновлено")
    except Exception as e:
        print(f"Ошибка обновления команд: {e}")

@dp.message(Command(commands='start'))
async def addTask(message: types.Message, state: FSMContext):
    welcome_text = """
        Привет! Я бот, который помогает с задачами.

        Доступные команды:
        /add — добавить новую задачу
        /tasks - список задач
        /help — справка (еще не работает)
        /cat — получить случайное фото котика

        Deep down, I'am clown!
        """
    await message.answer(welcome_text)

async def get_tasks(user_id: int):
    """Возвращает список задач пользователя"""
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT task FROM tasks WHERE user_id = ? ORDER BY created_at",
            (user_id,)
        )
        rows = await cursor.fetchall()
        return [row[0] for row in rows]

@dp.message(Command(commands='add'))
async def addTask(message: types.Message, state: FSMContext):
    await message.answer('Напиши текст задачи:')
    await state.set_state(States.task_state)
    current_state = await state.get_state()
    print(current_state)

@dp.message(Command(commands='delete'))
async def deleteTask(message: types.Message, state: FSMContext):
    await message.answer('Укажите номер задачи дял удаления:')
    await printTask(message, state)
    await state.set_state(States.delete_state)
    current_state = await state.get_state()
    print(current_state)

@dp.message(Command(commands='tasks'))
async def printTask(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    res: list
    res = await get_tasks(int(user_id))
    if res:
        await message.answer('\n'.join([f'{i + 1}. {item}' for i, item in enumerate(res)]))
    else:
        await message.answer('Нет задач')
    

@dp.message(Command(commands='clear_task'))
async def clearTask(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await clear_task(int(user_id))

@dp.message(Command(commands='cat'))
async def send_cat(message: types.Message):
    async with aiohttp.ClientSession() as session:
        async with session.get(CATS_URL) as resp:
            if resp.status == 200:
                data = await resp.json()
                cat_url = data[0]['url']
                await message.answer_photo(cat_url, caption="Вот тебе котик!")
            else:
                await message.answer("Не удалось получить котика 😿")

@dp.message(States.delete_state)
async def process_delete(message: types.Message, state: FSMContext):
    user_id = int(message.from_user.id)
    number = int(message.text)
    async with aiosqlite.connect(DB_NAME) as db:
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
            await message.answer("Неверный номер")
    await state.clear()

@dp.message(States.task_state)
async def process_task(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    task = message.text
    await add_task(int(user_id), task)
    await message.answer(f'Задача "{task}" добавлена!')
    await state.clear()   # выходим из состояния
    print("Состояние очищено")


async def reminder():
    while True:
        await asyncio.sleep(20)
        async with aiosqlite.connect(DB_NAME) as db:
            cursor = await db.execute("SELECT DISTINCT user_id FROM tasks")
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
                    task_list = "\n".join(f"{t[0]}" for t in tasks)
                    text = f"🔔 Напоминание о задачах:\n{task_list}"
                    
                    try:
                        await bot.send_message(chat_id=user_id, text=text)
                    except Exception as e:
                        # Пользователь мог заблокировать бота или другая ошибка
                        print(f"Не удалось отправить напоминание пользователю {user_id}: {e}")
                        # Опционально: удалить задачи этого пользователя
                        # await db.execute("DELETE FROM tasks WHERE user_id = ?", (user_id,))
                        # await db.commit()
                
                await asyncio.sleep(0.1)  # пауза между отправками            
        

async def main():
    await init_db()
    asyncio.create_task(reminder())
    await setup_commands()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())