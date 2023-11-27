from datetime import datetime
from typing import NamedTuple
from vk_api import VkUpload
from vk_api.exceptions import ApiError
import requests
from io import BytesIO


class VkMedia(NamedTuple):
    url: str
    type: str


# def resend_to_vk(vk_session, vk_group_id, message, media_group=None):
#     vk = vk_session.get_api()
#     vk_upload = VkUpload(vk)
#
#     if media_group:
#         attachments = []
#         try:
#             for media in media_group:
#                 if media["type"] == "photo":
#                     photo = vk_upload.photo_wall(
#                         photos=media["src"], group_id=vk_group_id * -1
#                     )
#                     attachments.append(
#                         "photo{}_{}_{}".format(
#                             photo[0]["owner_id"], photo[0]["id"], photo[0]["access_key"]
#                         )
#                     )
#                 elif media["type"] == "video":
#                     video = vk_upload.video(
#                         video_file=media["src"], group_id=vk_group_id * -1
#                     )
#                     attachments.append(
#                         "video{}_{}".format(video["owner_id"], video["video_id"])
#                     )
#             post_data = vk.wall.post(
#                 message=message.caption,
#                 owner_id=vk_group_id,
#                 from_group=1,
#                 attachments=attachments,
#             )
#         except ApiError as e:
#             print("vkapi err", e)
#             post_data = vk.wall.post(
#                 message=message.caption, owner_id=vk_group_id, from_group=1
#             )
#     else:
#         post_data = vk.wall.post(
#             message=message.text, owner_id=vk_group_id, from_group=1
#         )
#     print(
#         f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] New post published №{post_data['post_id']}"
#     )


def resend_to_vk(vk_session, vk_group_id, message, media: VkMedia):
    vk = vk_session.get_api()
    vk_upload = VkUpload(vk)

    img = requests.get(media.url).content
    f = BytesIO(img)
    try:
        if media.type == "photo":
            response = vk_upload.photo_wall(f, group_id=vk_group_id * -1)[0]
            owner_id, photo_id, access_key = (
                response["owner_id"],
                response["id"],
                response["access_key"],
            )
            attachments = f"photo{owner_id}_{photo_id}_{access_key}"
        elif media.type == "video":
            response = vk_upload.video(f, group_id=vk_group_id * -1)[0]
            owner_id, video_id, access_key = (
                response["owner_id"],
                response["id"],
                response["access_key"],
            )
            attachments = f"video{owner_id}_{video_id}_{access_key}"
        post_data = vk.wall.post(
            message=message,
            owner_id=vk_group_id,
            from_group=1,
            attachments=attachments,
        )
    except ApiError as e:
        print("vkapi err", e)
        post_data = vk.wall.post(message=message, owner_id=vk_group_id, from_group=1)
    else:
        post_data = vk.wall.post(
            message=message.text, owner_id=vk_group_id, from_group=1
        )
    print(
        f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] New post published №{post_data['post_id']}"
    )
