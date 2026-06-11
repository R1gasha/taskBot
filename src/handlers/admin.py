from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from database import *
from fsm_states import States
from aiogram import F
import aiohttp
from config import HOST_METRIC, PORT_METRIC
from prometheus_client.parser import text_string_to_metric_families

# Список ID администраторов (можно также брать из БД)
ADMIN_IDS = {391912003}

router = Router()

# Фильтр на уровне роутера – все хендлеры в этом роутере будут доступны только админам
router.message.filter(F.from_user.id.in_(ADMIN_IDS))

@router.message(Command('metrics'))
async def cmd_metrics(message: types.Message):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'http://{HOST_METRIC}:{PORT_METRIC}/metrics') as resp:
            if resp.status != 200:
                await message.answer('Ошибка получения метрик')
                return
            text = await resp.text()

    metrics = {
        'telemt_user_connections_current': 0,
        'telemt_user_unique_ips_current':0,
        'telemt_user_unique_ips_limit': 0,
        'telemt_user_unique_ips_utilization': 0,
    }

    target_user = 'hello'

    for family in text_string_to_metric_families(text):
        for sample in family.samples:
            if sample.labels.get('user') == target_user:
                if sample.name in metrics:
                    metrics[sample.name] = sample.value

    res = (f"{key} - {value}" for key, value in metrics.items())

    await message.answer('\n'.join(res))




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

@router.message(Command('add_magnit'))
async def cmd_admin(message: types.Message, state: FSMContext):
    await message.answer('Доставай все что есть!')
    await state.set_state(States.magnit_state)
    current_state = await state.get_state()
    print(current_state)

@router.message(Command(commands='get_links'))
async def printTask(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    res: list
    res = await magnit_manager.get_all(int(user_id))
    if res:
        await message.answer('\n'.join([f'{i + 1}. {item}' for i, item in enumerate(res)]))
    else:
        await message.answer('Ничего не добавили еще...')


@router.message(Command(commands='delete_magnit'))
async def deleteTask(message: types.Message, state: FSMContext):
    await message.answer('Укажите номер ссылки для удаления:')
    await printTask(message, state)
    await state.set_state(States.delete_state)
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
    await magnit_manager.add(int(user_id), link)
    await message.answer(f'Что-то новенькое? А, я понял!')
    await state.clear() 
    print("Состояние очищено")    


@router.message(States.delete_magnit_state)
async def process_delete(message: types.Message, state: FSMContext):
    user_id = int(message.from_user.id)
    number = int(message.text)
    res = await magnit_manager.delete(user_id, number)
    if res:
        await message.answer(f'Ссылка удалена!')
    else:
        await message.answer(f'Невозможно удалить ссылку!')
    await state.clear()
    print("Состояние очищено")  