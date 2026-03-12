from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import BotCommand
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram.types import FSInputFile
import aiohttp
import asyncio
from config import BOT_TOKEN
from remainder import reminder
from database import *
import os


class States(StatesGroup):
    task_state = State()
    delete_state = State()
    timer_state = State()


CATS_URL = 'https://api.thecatapi.com/v1/images/search'

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

async def setup_commands():
    commands = [
        BotCommand(command="start", description="Информация"),
        BotCommand(command="add", description="Добавить задачу"),
        BotCommand(command="tasks", description="Список задач"),
        BotCommand(command="cat", description="Посмотреть на котика"),
        BotCommand(command="delete", description="Убрать задачу"),
        BotCommand(command="timer", description="Частота напоминаний"),
        BotCommand(command="clear_task", description="Очистить все задачи"),
    ]
    try:
        await bot.set_my_commands(commands)
        print("Меню команд обновлено")
    except Exception as e:
        print(f"Ошибка обновления команд: {e}")

@dp.message(Command(commands='start'))
async def start(message: types.Message, state: FSMContext):
    welcome_text = """
        Меня зовут Глути! Я всего лишь стажер.
        Разработаем приложение?

        Доступные команды:
        /add — добавить новую задачу
        /tasks - список задач
        /help — справка (еще не работает)
        /cat — получить случайное фото котика

        """
    print('Start')
    photo = FSInputFile('src/img/gluty.jpg')
    await bot.send_photo(chat_id=message.chat.id,  photo=photo,caption = welcome_text)
    #await message.answer(welcome_text)

@dp.message(Command(commands='add'))
async def addTask(message: types.Message, state: FSMContext):
    await message.answer('Напиши текст задачи:')
    await state.set_state(States.task_state)
    current_state = await state.get_state()
    print(current_state)

@dp.message(Command(commands='timer'))
async def addTimer(message: types.Message, state: FSMContext):
    await message.answer('Установим мою частоту напоминаний:')
    await state.set_state(States.timer_state)
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
    await message.answer('Задачи выполнены! Ты молодец!\nА я всего лишь стажер!')

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
    res = await delete_task(user_id, number)
    if res:
        await message.answer(f'Задача удалена!')
    else:
        await message.answer(f'Невозможно удалить задачу!')
    await state.clear()
    print("Состояние очищено")  

@dp.message(States.timer_state)
async def proccess_timer(message: types.Message, state: FSMContext):
    user_id = int(message.from_user.id)
    try:
        timer = int(message.text)
    except ValueError:
        await message.answer(f'Введите корректное число, а то не разработаем приложение')
        return
    await add_timer(user_id, timer)
    await state.clear()
    print("Состояние очищено")  

@dp.message(States.task_state)
async def process_task(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    task = message.text
    await add_task(int(user_id), task)
    await message.answer(f'Задача "{task}" добавлена!')
    await state.clear()   # выходим из состояния
    print("Состояние очищено")         
        

async def main():
    await init_db()
    #asyncio.create_task(reminder(bot))
    await setup_commands()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())