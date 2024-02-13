import handler
import asyncio
from pyrogram.sync import idle
import censor_bot


if __name__ == "__main__":
    print("Бот запущен")
    handler.scheduler.start()
    loop = asyncio.get_event_loop()
    loop.create_task(handler.start())
    loop.create_task(censor_bot.run())
    handler.client.start()
    idle()
