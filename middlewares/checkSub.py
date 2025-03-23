import logging
import sqlite3
from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from utils.misc import subscription
from loader import dp, bot, channel as channeldb
import json
from data.config import ADMINS
import asyncio

conn = sqlite3.connect("requests.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS requests (
        user_id INTEGER PRIMARY KEY,
        status TEXT
    )
""")
conn.commit()

class BigBrother(BaseMiddleware):
    async def on_pre_process_update(self, update: types.Update, data: dict):
        if update.message:
            user = update.message.from_user.id
            args = update.message.get_args() if update.message.get_args() else "None"
        elif update.callback_query:
            user = update.callback_query.from_user.id
            args = "None"
            if update.callback_query.data.startswith('check_subs'):
                args = update.callback_query.data.split(":")[1]
                await update.callback_query.message.delete()
        else:
            return
        if user in ADMINS:
            return
        buttons = InlineKeyboardMarkup(row_width=1)
        final_status = True
        request_needed = False
        CHANNELS = channeldb.get_channels()
        
        for channel_data in CHANNELS:
            channel_info = json.loads(channel_data)
            channel_id = channel_info["id"]
            mode = channel_info["mode"]

            if mode == "request":
                cursor.execute("SELECT status FROM requests WHERE user_id = ?", (user,))
                result = cursor.fetchone()

                if not result or result[0] != "approved":
                    request_link = await bot.create_chat_invite_link(chat_id=channel_id, creates_join_request=True)
                    print(request_link)
                    buttons.add(InlineKeyboardButton(text="🔗 Zayavka yuborish", url=request_link['invite_link']))
                    request_needed = True
                
            else:
                status = await subscription.check(user_id=user, channel=channel_id)
                
                if not status:
                    final_status = False
                    invite_link = await bot.export_chat_invite_link(channel_id)
                    buttons.add(InlineKeyboardButton(text="🔗 Kanalga kirish", url=invite_link))

        if request_needed or not final_status:
            buttons.add(InlineKeyboardButton(text="✅ Obuna bo'ldim", callback_data=f"check_subs:{args}"))
            
            if update.message:
                await update.message.answer('⚠️ Botdan foydalanish uchun quyidagi kanallarga obuna bo‘ling:', reply_markup=buttons)
            else:
                await update.callback_query.message.answer('⚠️ Botdan foydalanish uchun quyidagi kanallarga obuna bo‘ling:', reply_markup=buttons)
            
            raise CancelHandler()

@dp.chat_join_request_handler()
async def handle_join_request(event: types.ChatJoinRequest):
    user_id = event.from_user.id
    cursor.execute("INSERT OR REPLACE INTO requests (user_id, status) VALUES (?, ?)", (user_id, "pending"))
    conn.commit()
    await approve_user(user_id)

async def approve_user(user_id: int):
    cursor.execute("UPDATE requests SET status = ? WHERE user_id = ?", ("approved", user_id))
    conn.commit()
