from typing import NamedTuple


class Post(NamedTuple):
    url: str | None
    type: str
    text: str


class VkGroup(NamedTuple):
    group_id: str
    token: str
