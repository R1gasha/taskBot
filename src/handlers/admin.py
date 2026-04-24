from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from database import *
from fsm_states import States
from aiogram import F

# Список ID администраторов (можно также брать из БД)
ADMIN_IDS = {391912003}

router = Router()

# Фильтр на уровне роутера – все хендлеры в этом роутере будут доступны только админам
router.message.filter(F.from_user.id.in_(ADMIN_IDS))

@router.message(lambda message: message.sticker)
async def cmd_admin(message: types.Message):
    print(message.sticker.file_id)
    await message.answer(message.sticker.file_id)

@router.message(Command('admin_help'))
async def cmd_admin(message: types.Message):
    text_ = """
    Полезнаю информация:
    - Инитком 201-27-97
    - Дубль В 221-91-91

    """
    await message.answer(text_)

@router.message(Command('magnit'))
async def cmd_admin(message: types.Message, state: FSMContext):
    await message.answer('Доставай все что есть!')
    await state.set_state(States.magnit_state)
    current_state = await state.get_state()
    print(current_state)

@router.message(Command(commands='timer'))
async def addTimer(message: types.Message, state: FSMContext):
    await message.answer('Установим мою частоту напоминаний:')
    await state.set_state(States.timer_state)
    current_state = await state.get_state()
    print(current_state)

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

@router.message(States.magnit_state)
async def process_task(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    link = message.text
    await add_magnit(int(user_id), link)
    await message.answer(f'Что-то новенькое? А, я понял!')
    await state.clear() 
    print("Состояние очищено")    