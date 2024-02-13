import logging


from pyrogram.enums import ParseMode
from pyrogram.client import Client
from vk_api import VkApi

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
    for post in get_info_from_newbryansk():
        if post is not None:
            logging.warning(post)
            try:
                await client.send_photo(
                    id, post.url, caption=post.text, parse_mode=ParseMode.HTML
                )
            except Exception:
                await client.send_photo(id, post.url)
                await client.send_message(id, post.text, parse_mode=ParseMode.HTML)
            print(config.VK_BR.token)
            vk_session, vk_group_id = (
                VkApi(token=config.VK_BR.token),
                config.VK_BR.group_id,
            )
            resend_to_vk(vk_session, vk_group_id, post)


async def send_info_ria_polling(id, client):
    logging.warning("Выполняю RIA")
    post = get_info_from_ria()
    logging.warning(post)
    if post is not None:
        ext = post.url.split(".")[-1]  # type:ignore
        if ext not in photo_ext:
            await client.send_video(
                id, post.url, caption=post.text, parse_mode=ParseMode.HTML
            )
        else:
            await client.send_photo(
                id, post.url, caption=post.text, parse_mode=ParseMode.HTML
            )
        for group in [config.VK_MSK, config.VK_SPB]:
            print(group.token)
            vk_session, vk_group_id = VkApi(token=group.token), group.group_id
            resend_to_vk(vk_session, vk_group_id, post)


async def send_info_bga_polling(id, client):
    logging.warning("Выполняю БГ")
    post = get_info_from_bga()
    logging.warning(post)
    if post is not None:
        try:
            if post.url is not None:
                await client.send_photo(
                    id, post.url, caption=post.text, parse_mode=ParseMode.HTML
                )
            else:
                await client.send_message(id, post.text, parse_mode=ParseMode.HTML)
        except Exception:
            if post.url is not None:
                await client.send_photo(id, post.url)
            await client.send_message(id, post.text, parse_mode=ParseMode.HTML)
        logging.warning(config.VK_BR.token)
        vk_session, vk_group_id = VkApi(token=config.VK_BR.token), config.VK_BR.group_id
        resend_to_vk(vk_session, vk_group_id, post)


async def send_info_bo_polling(id, client):
    logging.warning("Выполняю BO")
    post = get_info_from_bryanskobl()
    logging.warning(post)
    if post is not None:
        try:
            if post.url is not None:
                await client.send_photo(
                    id, post.url, caption=post.text, parse_mode=ParseMode.HTML
                )
            else:
                await client.send_message(id, post.text, parse_mode=ParseMode.HTML)
        except Exception:
            await client.send_photo(id, post.url)
            await client.send_message(id, post.text, parse_mode=ParseMode.HTML)
        logging.warning(config.VK_BR.token)
        vk_session, vk_group_id = VkApi(token=config.VK_BR.token), config.VK_BR.group_id
        resend_to_vk(vk_session, vk_group_id, post)


async def send_info_gub_polling(id, client):
    logging.warning("Выполняю GUB")
    for post in get_info_from_gub():
        if post is not None:
            logging.warning(post)
            try:
                if post.url is not None:
                    ext = post.url.split(".")[-1]
                    if ext not in photo_ext:
                        await client.send_video(
                            id,
                            post.url,
                            caption=post.text,
                            parse_mode=ParseMode.HTML,
                        )
                    else:
                        await client.send_photo(
                            id,
                            post.url,
                            caption=post.text,
                            parse_mode=ParseMode.HTML,
                        )
                else:
                    await client.send_message(id, post.text, parse_mode=ParseMode.HTML)
            except Exception:
                await client.send_photo(id, post.url)
                await client.send_message(id, post.text, parse_mode=ParseMode.HTML)
            logging.warning(config.VK_BR.token)
            vk_session, vk_group_id = (
                VkApi(token=config.VK_BR.token),
                config.VK_BR.group_id,
            )
            resend_to_vk(vk_session, vk_group_id, post)


async def send_info_brgaz_polling(id, client):
    logging.warning("Выполняю BRGAZ")
    post = get_info_from_brgaz()
    logging.warning(post)
    if post is not None:
        try:
            await client.send_photo(
                id, post.url, caption=post.text, parse_mode=ParseMode.HTML
            )
        except Exception:
            await client.send_photo(id, post.url)
            await client.send_message(id, post.text, parse_mode=ParseMode.HTML)
        logging.warning(config.VK_BR.token)
        vk_session, vk_group_id = VkApi(token=config.VK_BR.token), config.VK_BR.group_id
        resend_to_vk(vk_session, vk_group_id, post)


async def send_info_bn_polling(id, client):
    logging.warning("Выполняю BN")
    post = get_info_from_bn()
    logging.warning(post)
    if post is not None:
        try:
            await client.send_photo(
                id, post.url, caption=post.text, parse_mode=ParseMode.HTML
            )
        except Exception:
            await client.send_photo(id, post.url)
            await client.send_message(id, post.text, parse_mode=ParseMode.HTML)
        logging.warning(config.VK_BR.token)
        vk_session, vk_group_id = VkApi(token=config.VK_BR.token), config.VK_BR.group_id
        resend_to_vk(vk_session, vk_group_id, post)


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
    scheduler.start()
