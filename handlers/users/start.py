from filters.private_chat_filter import IsPrivate
import sqlite3
from data import config
from aiogram import types

from data.config import ADMINS, BOT_NAME, BOT_HANDLE, OFFICIAL_CHANNEL
from keyboards.default.buttons import main, back, movie_details_keyboard
from loader import dp, db, bot
from aiogram.dispatcher import FSMContext
from .main import back_movie
from loader import ratings_db, movie_db
from aiogram.types import InputMediaPhoto



    
@dp.callback_query_handler(text_contains="check_subs", state="*")
async def check_subs(call: types.CallbackQuery, state:FSMContext):
    try:
        db.add_user(id=call.from_user.id, fullname=call.from_user.full_name)
    except:
        pass
    movie_id = call.data.split(":")[1]
    movie_id = movie_id.replace("movie_", '')
    movie_data = movie_db.get_movie(movie_id=movie_id)
    if movie_data is not None:
        poster_url = movie_data['poster']
        user_data = ratings_db.get_user_current_status(user_id=call.from_user.id, movie_id=movie_id)
        selfrating = ratings_db.get_rating_movie(movie_id=movie_id)['average_rating'] if ratings_db.get_rating_movie(movie_id=movie_id) is not None else "0"
        ratings_db.update_views(movie_id=movie_id, user_id=call.from_user.id)
        views = ratings_db.get_views(movie_id=movie_id)

        if movie_data['type'] == 'movie':
            await call.message.answer_photo(
                photo=poster_url, 
                caption=f"🎬 <b>{movie_data['name'].capitalize()}\n\n</b>"
                            f"<b>⭐️ IMDb:</b> {movie_data['imdb']} | KinoPisk: {movie_data['kinopoisk']} | {BOT_NAME}: {selfrating}\n"
                                f"<b>👁 Ko'rishlar soni:</b> {views}\n"
                                f"<b>📆 Yil:</b> {movie_data['year']}\n"  
                                f"<b>🌐 Davlat:</b> {movie_data['country'].capitalize()}\n"
                                f"<b>🎭 Janri:</b> {', '.join(genre.title() for genre in movie_data['genres'])}\n"
                                f"<b>🛎 Rejissorlar:</b> {', '.join(director.title() for director in movie_data['directors'])}\n"
                                f"<b>👨‍🎤 Aktyorlar:</b> {', '.join(actor.title() for actor in movie_data['actors'])}\n"
                                f"<b>ℹ️ Tavsif:</b> <blockquote expandable><span class='tg-spoiler'>{movie_data['detailed_info'].capitalize()}</span></blockquote>\n"
                                f"<b>🟡 Trailer:</b> <a href='{movie_data['trailer_url']}'> bu yerga bosing</a>\n"
                                f"➖➖➖➖➖➖➖➖➖➖➖\n"
                                f"<b>✈️ Kanalimiz:</b> @{OFFICIAL_CHANNEL}\n"
                                f"<b>🤖 Botimiz:</b> @{BOT_HANDLE}",                               
                reply_markup=movie_details_keyboard(movie_id=movie_id, watchlist=user_data['watchlist'], saved=user_data['saved'], favourite=user_data['favourite'], type="movie"))

        else:
            total_episodes = movie_data['total_episodes']
            total_seasons = movie_data['total_seasons']



            await call.message.answer_photo(
                photo=poster_url, 
                caption=f"🎬 <b>{movie_data['name']}</b>\n\n"
                            f"<b>⭐️ IMDb:</b> {movie_data['imdb']} | KinoPisk: {movie_data['kinopoisk']} | {BOT_NAME}: {selfrating}\n"
                                f"<b>👁 Ko'rishlar soni:</b> {views}\n"
                                f"<b>📆 Yil:</b> {movie_data['year']}\n"  
                                f"<b>🌐 Davlat:</b> {movie_data['country'].capitalize()}\n"
                                f"<b>🎭 Janri:</b> {', '.join(genre.title() for genre in movie_data['genres'])}\n"
                                f"<b>🛎 Rejissorlar:</b> {', '.join(director.title() for director in movie_data['directors'])}\n"
                                f"<b>👨‍🎤 Aktyorlar:</b> {', '.join(actor.title() for actor in movie_data['actors'])}\n"
                                f"<b>ℹ️ Tavsif:</b> <blockquote expandable><span class='tg-spoiler'>{movie_data['detailed_info'].capitalize()}</span></blockquote>\n"
                                f"<b>🟡 Trailer:</b> <a href='{movie_data['trailer_url']}'> bu yerga bosing</a>\n"
                                f"👉 {total_episodes} ta qism, {total_seasons} ta sezon\n"
                                f"➖➖➖➖➖➖➖➖➖➖➖\n"
                                f"<b>✈️ Kanalimiz:</b> @{OFFICIAL_CHANNEL}\n"
                                f"<b>🤖 Botimiz:</b> @{BOT_HANDLE}",
                reply_markup=movie_details_keyboard(movie_id=movie_id, watchlist=user_data['watchlist'], saved=user_data['saved'], favourite=user_data['favourite'], type="tv_series")

            )

    else:
        await state.finish()
        await call.message.answer_photo(
            config.MAIN_PHOTO,
            caption=f"<b>👋 Assalomu alaykum <a href='tg://user?id={call.from_user.id}'>{call.from_user.full_name}</a>, platformaga xush kelibsiz!</b>\n\n<i>✌️ Bot orqali eng so'nggi premyeralar va top reytingli kinolarni topishingiz mumkin!</i>\n\n👇 Quyidagi menudan kerakli bo'limni tanlang!",
            reply_markup=main
        )



