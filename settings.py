import logging
from pydantic_settings import BaseSettings, SettingsConfigDict

from mytypes import VkGroup


class ConfigBase(BaseSettings):
    model_config = SettingsConfigDict(env_file=f".env", extra="ignore")


# fmt: off
class Config(ConfigBase):
    BOT_TOKEN:         str = ''
    API_ID:            str = ''
    API_HASH:          str = ''
    WEATHER_API_KEY:   str = ''
    
    CHANNEL_ID:        int = 0
    COMMENT_GROUP_ID:  int = 0 
    MOSCOW_CHANNEL_ID: int = 0
    
    MCHS:              str = ''
    WEATHER :          str = ''
    HOLY:              str = ''
    NEWBR:             str = ''
    RIA:               str = ''
    BGA:               str = ''
    BO:                str = ''
    GUB_ACS:           str = ''
    GUB_CRMNL:         str = ''
    BRGAZ:             str = ''
    BN:                str = ''
    
    VK_MSK_ID:         str = ''
    VK_MSK_TOKEN:      str = ''
    VK_MSK: VkGroup | None = None
    VK_SPB_ID:         str = ''
    VK_SPB_TOKEN:      str = ''
    VK_SPB: VkGroup | None = None
    VK_BR_ID:          str = ''
    VK_BR_TOKEN:       str = ''
    VK_BR:  VkGroup | None = None

    REDIS_HOST:        str = 'localhost'
    REDIS_PORT:        int = 6379

    def __post_init__(self):
        self.VK_MSK = VkGroup(self.VK_MSK_ID, self.VK_MSK_TOKEN)
        self.VK_SPB = VkGroup(self.VK_SPB_ID, self.VK_SPB_TOKEN)
        self.VK_BR = VkGroup(self.VK_BR_ID, self.VK_BR_TOKEN)
# fmt: on

config = Config()
config.__post_init__()
