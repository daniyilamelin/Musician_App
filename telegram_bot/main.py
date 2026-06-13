import asyncio
from aiogram import Dispatcher, Bot
from handlers import music_router
import os


bot = Bot(token = os.getenv("BOT_TOKEN"))

dp = Dispatcher()

async def main():
    dp.include_router(music_router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Зупинено користувачем")
    except Exception as e:
        print(f"\n❌ Помилка: {e}")