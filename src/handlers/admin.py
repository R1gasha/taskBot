from aiogram import Router, types
from aiogram.filters import Command
import aiohttp
from aiogram import F

# Список ID администраторов (можно также брать из БД)
ADMIN_IDS = {391912003}
CATS_URL = 'https://api.thecatapi.com/v1/images/search'

router = Router()

# Фильтр на уровне роутера – все хендлеры в этом роутере будут доступны только админам
router.message.filter(F.from_user.id.in_(ADMIN_IDS))

@router.message(Command('admin'))
async def cmd_admin(message: types.Message):
    await message.answer("Панель администратора")

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

# @router.message(Command('stats'))
# async def cmd_stats(message: types.Message):
#     await message.answer("Статистика для админа")