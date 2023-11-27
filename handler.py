import logging


from pyrogram.enums import ParseMode
from pyrogram.client import Client

from parsing import (
    get_info_from_bga,
    get_info_from_bn,
    get_info_from_brgaz,
    get_info_from_bryanskobl,
    get_info_from_gub,
    get_info_from_newbryansk,
    get_info_from_ria,
    get_urgent_information,
    get_urgent_information_polling,
)
from settings import config
from pyrogram.client import Client
from settings import config
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from vk import resend_to_vk

scheduler = AsyncIOScheduler(timezone="UTC")


client = Client(":memory:", config.API_ID, config.API_HASH)


photo_ext = ["jpg", "jpeg", "png", "webp"]


async def get_session():
    session = await client.export_session_string()
    return session


async def send_urgent_info(id, client):
    ads: dict | None = get_urgent_information()
    message = "Сводка новостей за прошедшие сутки\n\n"
    if ads is not None:
        for ad in ads.items():
            message += f"{ad[0]}\n{ad[1]}\n\n"
        await client.send_message(id, message, parse_mode=ParseMode.HTML)


async def send_info_polling(id, client):
    logging.warning("Выполняю INFO")
    thing = get_urgent_information_polling()
    if thing is not None:
        try:
            photo = "images/mchs.jpg"
            await client.send_photo(id, photo, caption=thing, parse_mode=ParseMode.HTML)
        except Exception as e:
            logging.error("Слишком длинное сообщение")
            logging.error(e)
            photo = "images/mchs.jpg"
            await client.send_photo(id, photo)
            await client.send_message(id, thing, parse_mode=ParseMode.HTML)


async def send_info_newbryansk_polling(id, client):
    logging.warning("Выполняю NEWBR")
    for thing in get_info_from_newbryansk():
        try:
            if thing is not None:
                await client.send_photo(
                    id, thing[0], caption=thing[1], parse_mode=ParseMode.HTML
                )
                resend_to_vk()
        except Exception:
            if thing is not None:
                logging.info("Слишком длинное сообщение")
                await client.send_photo(id, thing[0])
                await client.send_message(id, thing[1], parse_mode=ParseMode.HTML)


async def send_info_ria_polling(id, client):
    logging.warning("Выполняю RIA")
    thing = get_info_from_ria()
    if thing is not None:
        ext = thing[0].split(".")[-1]
        if ext not in photo_ext:
            await client.send_video(
                id, thing[0], caption=thing[1], parse_mode=ParseMode.HTML
            )
            logging.warning("Видео")
        else:
            await client.send_photo(
                id, thing[0], caption=thing[1], parse_mode=ParseMode.HTML
            )
            logging.warning("Photo")


async def send_info_bga_polling(id, client):
    logging.warning("Выполняю БГ")
    thing = get_info_from_bga()
    try:
        if thing is not None:
            if thing[0] is not None:
                await client.send_photo(
                    id, thing[0], caption=thing[1], parse_mode=ParseMode.HTML
                )
            else:
                await client.send_message(id, thing[1], parse_mode=ParseMode.HTML)
    except Exception:
        if thing is not None:
            logging.info("Слишком длинное сообщение")
            if thing[0] is not None:
                await client.send_photo(id, thing[0])
            await client.send_message(id, thing[1], parse_mode=ParseMode.HTML)


async def send_info_bo_polling(id, client):
    logging.warning("Выполняю BO")
    thing = get_info_from_bryanskobl()
    try:
        if thing is not None:
            if thing[0] is not None:
                await client.send_photo(
                    id, thing[0], caption=thing[1], parse_mode=ParseMode.HTML
                )
            else:
                await client.send_message(id, thing[1], parse_mode=ParseMode.HTML)
    except Exception:
        if thing is not None:
            logging.info("Слишком длинное сообщение")
            await client.send_photo(id, thing[0])
            await client.send_message(id, thing[1], parse_mode=ParseMode.HTML)


async def send_info_gub_polling(id, client):
    logging.warning("Выполняю GUB")
    for thing in get_info_from_gub():
        try:
            if thing is not None:
                if thing[0] is not None:
                    ext = thing[0].split(".")[-1]
                    if ext not in photo_ext:
                        await client.send_video(
                            id,
                            thing[0],
                            caption=thing[1],
                            parse_mode=ParseMode.HTML,
                        )
                    else:
                        await client.send_photo(
                            id,
                            thing[0],
                            caption=thing[1],
                            parse_mode=ParseMode.HTML,
                        )
                else:
                    await client.send_message(id, thing[1], parse_mode=ParseMode.HTML)
        except Exception:
            logging.info("Слишком длинное сообщение")
            await client.send_photo(id, thing[0])
            await client.send_message(id, thing[1], parse_mode=ParseMode.HTML)


async def send_info_brgaz_polling(id, client):
    logging.warning("Выполняю BRGAZ")
    thing = get_info_from_brgaz()
    try:
        if thing is not None:
            await client.send_photo(
                id, thing[0], caption=thing[1], parse_mode=ParseMode.HTML
            )
    except Exception:
        if thing is not None:
            logging.info("Слишком длинное сообщение")
            await client.send_photo(id, thing[0])
            await client.send_message(id, thing[1], parse_mode=ParseMode.HTML)


async def send_info_bn_polling(id, client):
    logging.warning("Выполняю BN")
    thing = get_info_from_bn()
    try:
        if thing is not None:
            await client.send_photo(
                id, thing[0], caption=thing[1], parse_mode=ParseMode.HTML
            )
    except Exception:
        if thing is not None:
            logging.info("Слишком длинное сообщение")
            await client.send_photo(id, thing[0])
            await client.send_message(id, thing[1], parse_mode=ParseMode.HTML)


async def job(fid, mid):
    async with Client("bot", session_string=await get_session()):
        await send_info_polling(fid, client)
    async with Client("bot", session_string=await get_session()):
        await send_info_newbryansk_polling(fid, client)
    async with Client("bot", session_string=await get_session()):
        await send_info_ria_polling(mid, client)
    async with Client("bot", session_string=await get_session()):
        await send_info_bo_polling(fid, client)
    async with Client("bot", session_string=await get_session()):
        await send_info_gub_polling(fid, client)
    async with Client("bot", session_string=await get_session()):
        await send_info_brgaz_polling(fid, client)
    async with Client("bot", session_string=await get_session()):
        await send_info_bga_polling(fid, client)


async def start():
    cnl_id = config.CHANNEL_ID
    an_cnl_id = config.MOSCOW_CHANNEL_ID
    scheduler.add_job(
        job,
        "interval",
        args=[cnl_id, an_cnl_id],
        minutes=5,
        misfire_grace_time=None,
        max_instances=2,
    )
