import shutil, os
from vk_api import VkApi
from pyrogram import Client
from pyrogram.enums import MessageMediaType, ChatType

from vk import resend_to_vk
from config import API_ID, API_HASH, TG_BOT_TOKEN, TANDEMS

media_cache = []
app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=TG_BOT_TOKEN)
allow_chats = [item["tg_channel_id"] for item in TANDEMS]

@app.on_message()
async def message_handler(client, message):
    chat_id = message.chat.id
    if (chat_id > 0 or message.chat.type != ChatType.CHANNEL or chat_id not in allow_chats): return

    try:
        current_tandems = [tandem for tandem in TANDEMS if tandem["tg_channel_id"] == chat_id]
    except IndexError:
        return
    for current_tandem in current_tandems:
        vk_group_id = current_tandem["vk_group_id"]
        vk_session = VkApi(token=current_tandem["vk_token"])
        try:
            media_id = message.media_group_id

            if media_id:
                if media_id not in media_cache:
                    media_cache.append(media_id)
                    message_media = await client.get_media_group(chat_id, message.id)
                    media_group = []
                    for media_item in message_media:
                        src = await app.download_media(media_item)                    
                        media_group.append({
                            "type": "photo" if media_item.media == MessageMediaType.PHOTO else "video", 
                            "src": src
                        })
                    print(current_tandem)
                    resend_to_vk(vk_session, vk_group_id, message, media_group)
            else:
                media_group = [{"type": "photo" if message.media == MessageMediaType.PHOTO else "video", "src": await app.download_media(message)}]
                print(current_tandem)
                resend_to_vk(vk_session, vk_group_id, message, media_group)
        except ValueError:
            media_group = None
            resend_to_vk(vk_session, vk_group_id, message, media_group)

@app.on_disconnect()
async def disconnect_handler(_):
    if (os.path.exists("./downloads")):
        shutil.rmtree("./downloads", ignore_errors=False, onerror=None)

if __name__ == "__main__":
    print("Bot has been started...")
    app.run()
