from datetime import datetime
from vk_api import VkUpload
from vk_api.exceptions import ApiError
import requests
from io import BytesIO
from mytypes import Post


def resend_to_vk(vk_session, vk_group_id, post: Post):
    vk = vk_session.get_api()
    vk_upload = VkUpload(vk)

    img = requests.get(post.url).content  # type: ignore
    f = BytesIO(img)
    if post.url:
        try:
            if post.type == "photo":
                response = vk_upload.photo_wall(f, group_id=vk_group_id * -1)[0]
                owner_id, photo_id, access_key = (
                    response["owner_id"],
                    response["id"],
                    response["access_key"],
                )
                attachments = f"photo{owner_id}_{photo_id}_{access_key}"
            elif post.type == "video":
                response = vk_upload.video(f, group_id=vk_group_id * -1)[0]
                owner_id, video_id, access_key = (
                    response["owner_id"],
                    response["id"],
                    response["access_key"],
                )
                attachments = f"video{owner_id}_{video_id}_{access_key}"
            vk.wall.post(
                message=post.text,
                owner_id=vk_group_id,
                from_group=1,
                attachments=attachments,
            )
        except ApiError as e:
            print("vkapi err", e)
            vk.wall.post(message=post.text, owner_id=vk_group_id, from_group=1)
    else:
        vk.wall.post(message=post.text, owner_id=vk_group_id, from_group=1)
