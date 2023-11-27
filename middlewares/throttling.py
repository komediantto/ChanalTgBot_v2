import asyncio

from aiogram import Dispatcher, types
from aiogram.dispatcher import DEFAULT_RATE_LIMIT
from aiogram.dispatcher.handler import current_handler, CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import Throttled
from aiogram.types import MessageEntityType


class ThrottlingMiddleware(BaseMiddleware):
    """
    Simple middleware
    """

    def __init__(self, limit=DEFAULT_RATE_LIMIT, key_prefix='antiflood_'):
        self.rate_limit = limit
        self.prefix = key_prefix
        super(ThrottlingMiddleware, self).__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        """
        This handler is called when dispatcher receives a message

        :param message:
        """
        # Get current handler
        handler = current_handler.get()

        # Get dispatcher from context
        dispatcher = Dispatcher.get_current()
        # If handler was configured, get rate limit and key from handler
        if handler:
            limit = getattr(handler, 'throttling_rate_limit', self.rate_limit)
            key = getattr(
                handler, 'throttling_key', f"{self.prefix}_{handler.__name__}")
        else:
            limit = self.rate_limit
            key = f"{self.prefix}_message"

        # Use Dispatcher.throttle method.
        try:
            await dispatcher.throttle(key, rate=limit)
        except Throttled as t:
            # Execute action
            await self.message_throttled(message, t)

    async def message_throttled(self,
                                message: types.Message, throttled: Throttled):
        """
        Notify user only on first exceed
        and notify about unlocking only on last exceed

        :param message:
        :param throttled:
        """
        # Calculate how many time is left till the block ends
        delta = throttled.rate - throttled.delta

        # Prevent flooding
        if throttled.exceeded_count >= 2:
            await message.delete()

        # Sleep.
        await asyncio.sleep(delta)


# If the message contains a URL, delete the message and cancel the handler
# class UrlMiddleWare(BaseMiddleware):
#     async def on_pre_process_message(self, message: types.Message, data: dict):
#         if msg_entities := (message.entities or message.caption_entities):
#             for entitie in msg_entities:
#                 if entitie.type in [MessageEntityType.URL,
#                                     MessageEntityType.TEXT_LINK]:
#                     await message.delete()
#                     raise CancelHandler()
