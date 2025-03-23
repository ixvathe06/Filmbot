from filters.private_chat_filter import IsPrivate
import sqlite3

from aiogram import types
from aiogram.dispatcher import FSMContext
from data.config import ADMINS, BOT_NAME, BOT_HANDLE, OFFICIAL_CHANNEL
from loader import dp, db, bot, movie_db, ratings_db, genres_db
from aiogram.types.input_media import InputMediaVideo, InputMediaPhoto
from random import randint
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import requests
from aiogram.utils.exceptions import BadRequest


def is_valid_url(url):
    try:
        response = requests.head(url, allow_redirects=True)
        return response.status_code == 200
    except requests.RequestException:
        return False


@dp.inline_handler(state="*")
async def inline_query_handler(query: types.InlineQuery, state: FSMContext):
    await state.finish()
    text = query.query

    results = movie_db.search_movie(text)

    if text.startswith("genre:"):
        parts = text.replace("genre:", '')
        genre = parts.split(" ")
        if len(genre) == 2:
            results = movie_db.filter_genres(genre=genre[0], name=genre[1])
        else:
            results = movie_db.filter_genres(genre=genre[0])
    
    inline_answer = []
    count = 0

    for result in results:
        views = ratings_db.get_views(movie_id=result['movie_id'])

        text = (
            f"<a href='{result['poster_url']}'>🎬</a> <b>{result['name']}</b>\n\n"
            f"<b>👀 Ko'rishlar:</b> {views}\n<b>🌐 Davlat:</b> {result['country']}\n<b>📆 Yili:</b> {result['year']}\n<b>⏰ Davomiylik:</b> {result['duration']} soniya\n\n"
            f"<b>🔍 Kino kodi:</b> <code>{result['movie_id']}</code>\n\n"
            f"<b>🤖 Botimiz:</b> @ZaminFilmBot\n<b>📢 Kanalimiz:</b> @ZaminFilmRasmiy"

        )
        key = types.InlineKeyboardMarkup()
        key.add(
            types.InlineKeyboardButton("▶️ Kinoni ko'rish", url=f"https://t.me/{BOT_HANDLE}?start=movie_{result['movie_id']}")
        )
        key.add(
            types.InlineKeyboardButton("↪️ Ulashish", switch_inline_query=result['movie_id'])
        )       
        inline_answer.append(types.InlineQueryResultArticle(
                id=result['movie_id'],
                title=f"🎬 {result['name']}",
                thumb_url=result['poster_url'] if is_valid_url(result['poster_url']) else "https://i.imgur.com/ROgs7Du.png",
                input_message_content=types.InputTextMessageContent(
                    message_text=text,
                    parse_mode="HTML",
                    disable_web_page_preview=False
                ),
                description=f"👀 Ko'rishlar: {views}, 🌐 Davlat: {result['country']}, 📆 Yili: {result['year']}, ⏰ Davomiylik: {result['duration']}",
                reply_markup=key
            )
        )
        count+=1
        if count == 20:
            break
    if len(results) == 0:
        inline_answer.append(types.InlineQueryResultArticle(
            id=1,
            title=f"🔎 Natijalar topilmadi",
            input_message_content=types.InputTextMessageContent(message_text="Nat"),
        )
    )

    await query.answer(inline_answer, cache_time=5)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)