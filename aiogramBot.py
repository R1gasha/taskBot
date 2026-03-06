from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import BotCommand
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
import aiohttp
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()

class States(StatesGroup):
    task_state = State()


BOT_TOKEN = os.getenv('BOT_TOKEN')
CATS_URL = 'https://api.thecatapi.com/v1/images/search'

bot = Bot(BOT_TOKEN)
dp = Dispatcher()
tasks = {}

async def setup_commands():
    """Установка команд бота"""
    commands = [
        BotCommand(command="start", description="Информация"),
        BotCommand(command="add", description="Добавить задачу"),
        BotCommand(command="tasks", description="Список задач"),
        BotCommand(command="cat", description="Посмотреть на котика"),
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

@dp.message(Command(commands='add'))
async def addTask(message: types.Message, state: FSMContext):
    await message.answer('Напиши текст задачи:')
    await state.set_state(States.task_state)
    current_state = await state.get_state()
    print(current_state)

@dp.message(Command(commands='tasks'))
async def printTask(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    res: str
    if tasks.get(user_id):
        res = '\n'.join(tasks[user_id])
        await message.answer(res)
    else:
        await message.answer('Нет задач')
    

@dp.message(Command(commands='clear_task'))
async def clearTask(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    tasks[user_id].clear()

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

@dp.message(States.task_state)
async def process_task(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    task = message.text
    if user_id not in tasks:
        tasks[user_id] = []
    tasks[user_id].append(task)
    await message.answer(f'Задача "{task}" добавлена!')
    await state.clear()   # выходим из состояния
    print("Состояние очищено")

async def main():
    await setup_commands()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())