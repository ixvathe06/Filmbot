from aiogram import types
from aiogram.dispatcher.filters import BoundFilter


class IsPrivate(BoundFilter):
    async def check(self, message: types.Update):  
        try:return message.chat.type == types.ChatType.PRIVATE
        except:return message.message.chat.type == types.ChatType.PRIVATE
        