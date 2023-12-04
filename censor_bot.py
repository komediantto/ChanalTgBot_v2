import logging
import json
import string
from aiogram import Bot, Dispatcher, Router, types, F
from settings import config


bot: Bot = Bot(token=config.BOT_TOKEN, parse_mode="HTML")

dp: Dispatcher = Dispatcher()


router: Router = Router()


@router.message(F.chat.func(lambda chat: chat.id == config.COMMENT_GROUP_ID))
async def censorship(message: types.Message):
    """
    If the message contains a word from the list of forbidden words, then the
    message is deleted and the user is notified that the message was deleted

    :param message: types.Message - this is the message object that is passed
    to the function
    :type message: types.Message
    """
    logging.warning("Check!")
    if message.text:
        raw_message = message.text.replace("\n", " ")
        data = json.load(open("forbidden_words.json", encoding="utf-8"))
        profanity_list = []
        for i in data:
            profanity_list.append(i["word"])
        if {
            i.lower().translate(str.maketrans("", "", string.punctuation))
            for i in raw_message.split(" ")
        }.intersection(set(profanity_list)) != set():
            await message.reply("Маты запрещены")
            await message.delete()


dp.include_router(router)


async def run():
    logging.info("Start bot")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
