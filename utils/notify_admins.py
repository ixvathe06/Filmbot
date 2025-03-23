import logging

from aiogram import Dispatcher

from data.config import ADMINS


# async def on_startup_notify(dp: Dispatcher):
#     for admin in ADMINS:
#         try:
#             await dp.bot.send_message(admin, "✅Bot ishga tushdi.")
#         except Exception as err:
#             pass
async def on_shutdown_notify(dp: Dispatcher):
    for admin in ADMINS:
        try:
            await dp.bot.send_message(admin, "❌Bot ishlashdan to'xtadi.")
        except Exception as e:
            pass