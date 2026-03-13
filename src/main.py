from aiogram import Bot, Dispatcher, types
from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
from config import BOT_TOKEN
from remainder import reminder
from database import *
from handlers import common, admin
from handlers.admin import ADMIN_IDS

async def setup_commands(bot: Bot):
    common_commands = [
        BotCommand(command="start", description="Информация"),
        BotCommand(command="add", description="Добавить задачу"),
        BotCommand(command="tasks", description="Список задач"),
        BotCommand(command="delete", description="Убрать задачу"),
        BotCommand(command="timer", description="Частота напоминаний"),
        BotCommand(command="clear_task", description="Очистить все задачи"),
    ]
    admin_ =  [
        BotCommand(command="cat", description="Посмотреть на котика"),
        BotCommand(command="admin", description="Приветствую, Ад")
    ]

    admin_commands = common_commands + admin_

    try:
        for admin_id in ADMIN_IDS:
            await bot.set_my_commands(
                admin_commands,
                scope=BotCommandScopeChat(chat_id=admin_id)
        )
        print("Меню команд обновлено")
    except Exception as e:
        print(f"Ошибка обновления команд: {e}")   
        

async def main():
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(common.router)
    dp.include_router(admin.router)

    await init_db()
    #asyncio.create_task(reminder(bot))
    await setup_commands(bot)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())