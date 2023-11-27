from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigBase(BaseSettings):
    model_config = SettingsConfigDict(env_file=f".env", extra="ignore")


# fmt: off
class Config(ConfigBase):
    BOT_TOKEN:         str = ''
    API_ID:            str = ''
    API_HASH:          str = ''
    CHANNEL_ID:        int = 0
    COMMENT_GROUP_ID:  int = 0 
    MOSCOW_CHANNEL_ID: int = 0 
    WEATHER_API_KEY:   str = ''
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

    REDIS_HOST:        str = 'localhost'
    REDIS_PORT:        int = 6379
# fmt: on

config = Config()
