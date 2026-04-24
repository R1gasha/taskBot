from aiogram import Router, types
from aiogram.filters import Command
from aiogram import Bot
from aiogram.fsm.context import FSMContext
from database import *
from fsm_states import States
import aiohttp

router = Router()

CATS_URL = 'https://api.thecatapi.com/v1/images/search'

@router.message(Command(commands='start'))
async def start(message: types.Message, bot: Bot):
    id_sticker = 'CAACAgIAAxkBAAIDhWmzs90giCwqz-2_gC2TEqIdHsxvAAIlnQACe0aZSQABeYyOi-3XUzoE'
    welcome_text = """
        Меня зовут Глути! Я всего лишь стажер.

        Доступные команды:
        /add — добавить новую задачу
        /tasks - список задач
        /help — справка (еще не работает)
        /cat — получить случайное фото котика

        """
    await message.answer(welcome_text)
    await message.answer_sticker(id_sticker)

@router.message(Command(commands='add'))
async def addTask(message: types.Message, state: FSMContext):
    await message.answer('Напиши текст задачи:')
    await state.set_state(States.task_state)
    current_state = await state.get_state()
    print(current_state)

@router.message(Command(commands='delete'))
async def deleteTask(message: types.Message, state: FSMContext):
    await message.answer('Укажите номер задачи для удаления:')
    await printTask(message, state)
    await state.set_state(States.delete_state)
    current_state = await state.get_state()
    print(current_state)

@router.message(Command(commands='tasks'))
async def printTask(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    res: list
    res = await tasks_manager.get_all(int(user_id))
    if res:
        await message.answer('\n'.join([f'{i + 1}. {item}' for i, item in enumerate(res)]))
    else:
        await message.answer('Нет задач')
    

@router.message(Command(commands='clear_task'))
async def clearTask(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await tasks_manager.clear(int(user_id))
    await message.answer('Задачи выполнены! Ты молодец!\nА я всего лишь стажер!')


@router.message(States.delete_state)
async def process_delete(message: types.Message, state: FSMContext):
    user_id = int(message.from_user.id)
    number = int(message.text)
    res = await tasks_manager.delete(user_id, number)
    if res:
        await message.answer(f'Задача удалена!')
    else:
        await message.answer(f'Невозможно удалить задачу!')
    await state.clear()
    print("Состояние очищено")  

@router.message(States.task_state)
async def process_task(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    task = message.text
    await tasks_manager.add(int(user_id), task)
    await message.answer(f'Задача "{task}" добавлена!')
    await state.clear()   # выходим из состояния
    print("Состояние очищено")      

@router.message(Command(commands='cat'))
async def send_cat(message: types.Message):
    async with aiohttp.ClientSession() as session:
        async with session.get(CATS_URL) as resp:
            if resp.status == 200:
                data = await resp.json()
                cat_url = data[0]['url']
                await message.answer_photo(cat_url, caption="Вот тебе котик!")
            else:
                await message.answer("Не удалось получить котика 😿")