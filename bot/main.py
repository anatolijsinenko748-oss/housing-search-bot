import asyncio
import logging
from aiogram import Bot, Dispatcher
from database.db_helper import async_session_maker, engine
from handlers.search import router as search_router
from config import settings
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(dp: Dispatcher):

    yield

    await engine.dispose()

async def main():
    logging.basicConfig(level=logging.INFO)
    
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(search_router)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
    

