import asyncio
import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from bot_tools.handlers import router


DOTENV_PATH = '/root/.env'
load_dotenv(DOTENV_PATH)


async def main():
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()
    
    dp.include_router(router)
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())