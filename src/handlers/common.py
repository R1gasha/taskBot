from aiogram import Router, types
from aiogram.filters import Command
from aiogram import Bot
from aiogram.types import FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import *
from fsm_states import States

router = Router()

@router.message(Command(commands='start'))
async def start(message: types.Message, bot: Bot):
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

@router.message(Command(commands='add'))
async def addTask(message: types.Message, state: FSMContext):
    await message.answer('Напиши текст задачи:')
    await state.set_state(States.task_state)
    current_state = await state.get_state()
    print(current_state)

@router.message(Command(commands='timer'))
async def addTimer(message: types.Message, state: FSMContext):
    await message.answer('Установим мою частоту напоминаний:')
    await state.set_state(States.timer_state)
    current_state = await state.get_state()
    print(current_state)

@router.message(Command(commands='delete'))
async def deleteTask(message: types.Message, state: FSMContext):
    await message.answer('Укажите номер задачи дял удаления:')
    await printTask(message, state)
    await state.set_state(States.delete_state)
    current_state = await state.get_state()
    print(current_state)

@router.message(Command(commands='tasks'))
async def printTask(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    res: list
    res = await get_tasks(int(user_id))
    if res:
        await message.answer('\n'.join([f'{i + 1}. {item}' for i, item in enumerate(res)]))
    else:
        await message.answer('Нет задач')
    

@router.message(Command(commands='clear_task'))
async def clearTask(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await clear_task(int(user_id))
    await message.answer('Задачи выполнены! Ты молодец!\nА я всего лишь стажер!')


@router.message(States.delete_state)
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

@router.message(States.timer_state)
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

@router.message(States.task_state)
async def process_task(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    task = message.text
    await add_task(int(user_id), task)
    await message.answer(f'Задача "{task}" добавлена!')
    await state.clear()   # выходим из состояния
    print("Состояние очищено")      