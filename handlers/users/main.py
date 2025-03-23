from data import config
from filters.private_chat_filter import IsPrivate
import sqlite3

from aiogram import types
from aiogram.dispatcher import FSMContext
from data.config import ADMINS, BOT_NAME, BOT_HANDLE, OFFICIAL_CHANNEL
from keyboards.default.buttons import (main, back, movie_details_keyboard, quality_keyboard, 
                                       back_movie_keyboard, movie_list_keyboard, display_genres, 
                                       rating_keyboard_builder, episodes_watch_keyboard, episode_watch_keyboard,
                                       choose_quality_episode, back_season_keyboard)
from loader import dp, db, bot, movie_db, ratings_db, genres_db, db
from aiogram.types.input_media import InputMediaVideo, InputMediaPhoto

from pprint import pprint as print

@dp.message_handler(commands=["start"], state="*")
async def start_bot(message: types.Message, state: FSMContext):
    try:
        db.add_user(id=message.from_user.id, fullname=message.from_user.full_name)
    except:
        pass
    args = message.get_args()
    movie_id = args.replace("movie_", '')
    movie_data = movie_db.get_movie(movie_id=movie_id)
    if movie_data is not None:
        zaminfilm = ratings_db.get_rating_movie(movie_id=movie_id)['average_rating'] if ratings_db.get_rating_movie(movie_id=movie_id) is not None else "0"
        ratings_db.update_views(movie_id=movie_id, user_id=message.from_user.id)
        views = ratings_db.get_views(movie_id=movie_id)
        poster_url = movie_data['poster']
        user_data = ratings_db.get_user_current_status(user_id=message.from_user.id, movie_id=movie_id)
        if movie_data['type'] == 'movie':
            await message.answer_photo(
                photo=poster_url, 
                caption=f"🎬 <b>{movie_data['name'].capitalize()}\n\n</b>"
                                f"<b>⭐️ IMDb:</b> {movie_data['imdb']} | KinoPoisk: {movie_data['kinopoisk']} | {BOT_NAME}: {zaminfilm}\n"
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



            await message.answer_photo(
                photo=poster_url, 
                caption=f"🎬 <b>{movie_data['name']}</b>\n\n"
                                f"<b>⭐️ IMDb:</b> {movie_data['imdb']} | KinoPoisk: {movie_data['kinopoisk']} | {BOT_NAME}: {zaminfilm}\n"
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
        await message.answer_photo(
            config.MAIN_PHOTO,
            caption=f"<b>👋 Assalomu alaykum <a href='tg://user?id={message.from_user.id}'>{message.from_user.full_name}</a>, platformaga xush kelibsiz!</b>\n\n<i>✌️ Bot orqali eng so'nggi premyeralar va top reytingli kinolarni topishingiz mumkin!</i>\n\n👇 Quyidagi menudan kerakli bo'limni tanlang!",
            reply_markup=main
        )

@dp.callback_query_handler(text="back", state="*")
async def back_to_main(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    media = InputMediaPhoto(
        media=config.MAIN_PHOTO,
        caption=(
            f"<b>👋 Assalomu alaykum <a href='tg://user?id={callback.from_user.id}'>{callback.from_user.full_name}</a>, platformaga xush kelibsiz!</b>\n\n"
            "<i>✌️ Bot orqali eng so'nggi premyeralar va top reytingli kinolarni topishingiz mumkin!</i>\n\n"
            "👇 Quyidagi menudan kerakli bo'limni tanlang!"
        ),
        parse_mode="HTML"
    )

    await callback.message.edit_media(media, reply_markup=main)


@dp.callback_query_handler(text="search_movie", state="*")
async def search_movie(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await callback.message.edit_caption("🔍 Kinoni topish uchun kodni yuboring: ", reply_markup=back)

@dp.message_handler(state="*")
async def search_movie_handler(message: types.Message, state: FSMContext):
    movie_id = message.text

    try:
        splitted = message.text.split("\n")
        part = splitted[7].replace("🔍 Kino kodi: ", '')
        movie_id = int(part)
        await message.delete()
    except:
        pass
    if movie_db.get_movie(movie_id) is None:
        await message.answer("🎬 Kino kodi topilmadi, qaytadan urinib ko'ring: ", reply_markup=back)
        await state.set_state("search_movie")

    else:
        movie_data = movie_db.get_movie(movie_id)
        zaminfilm = ratings_db.get_rating_movie(movie_id=movie_id)['average_rating'] if ratings_db.get_rating_movie(movie_id=movie_id) is not None else "0"

        ratings_db.update_views(movie_id=movie_id, user_id=message.from_user.id)
        views = ratings_db.get_views(movie_id=movie_id)
        user_data = ratings_db.get_user_current_status(user_id=message.from_user.id, movie_id=movie_id)
        if movie_data['type'] == 'movie':
            await message.answer_photo(movie_data['poster'], caption=f"🎬 <b>{movie_data['name'].title()}\n\n</b>"
                                f"<b>⭐️ IMDb:</b> {movie_data['imdb']} | KinoPoisk: {movie_data['kinopoisk']} | {BOT_NAME}: {zaminfilm}\n"
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
                                f"<b>🤖 Botimiz:</b> @{BOT_HANDLE}", reply_markup=movie_details_keyboard(movie_id=movie_id, watchlist=user_data['watchlist'], saved=user_data['saved'], favourite=user_data['favourite'], type="movie")

)
        else:
            total_episodes = movie_data['total_episodes']
            total_seasons = movie_data['total_seasons']

            await message.answer_photo(movie_data['poster'], caption=f"🎬 <b>{movie_data['name']}</b>\n\n"
                            f"<b>⭐️ IMDb:</b> {movie_data['imdb']} | KinoPoisk: {movie_data['kinopoisk']} | {BOT_NAME}: {zaminfilm}\n"
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
                                f"<b>🤖 Botimiz:</b> @{BOT_HANDLE}", reply_markup=movie_details_keyboard(movie_id=movie_id, watchlist=user_data['watchlist'], saved=user_data['saved'], favourite=user_data['favourite'], type="tv_series")
)
        await state.finish()







@dp.callback_query_handler(text_contains="watch_movie", state="*")
async def select_quality(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    movie_id = callback.data.split(":")[1]
    movie_data = movie_db.get_movie(movie_id=movie_id)
    qualities = []

    text = f"🎬 <b>{movie_data['name']}</b>\n\n"

    for quality, details in movie_data["file_ids"].items():
        qualities.append(quality)
        size = details['size']
        text += f"🔰 <b>{quality}</b> — {size} MB\n"

    
    text += "\n📀 Kinoni ko'rish uchun sifatni tanlang!"

    await callback.message.edit_caption(text, reply_markup=quality_keyboard(movie_id, qualities))

@dp.callback_query_handler(text_contains="watch_tv_series", state="*")
async def select_quality(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    movie_id = callback.data.split(":")[1]
    movie_data = movie_db.get_movie(movie_id=movie_id)
    total_seasons = movie_data['total_seasons']
    if total_seasons == 1:
        episodes = movie_db.get_episodes(season=1, movie_id=movie_id)['episodes']
        text = f"🎬 <b>{movie_data['name']}</b>\n"

        text += "\n🔻 Filmni ko'rishda davom etish uchun qismni tanlang tanlang!"
        try:
            await callback.message.edit_caption(text, reply_markup=episode_watch_keyboard(movie_id, 1, episodes))
        except:
            await back_movie(callback, state)
        return

    text = f"🎬 <b>{movie_data['name']}</b>\n"

    text += "\n🔻 Filmni ko'rishda davom etish uchun sezonni tanlang!"

    await callback.message.edit_caption(text, reply_markup=episodes_watch_keyboard(movie_id, total_seasons))

@dp.callback_query_handler(text_contains="watch_season", state="*")
async def select_quality(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    movie_id = callback.data.split(":")[1]
    season = callback.data.split(":")[2]
    episode_data = movie_db.get_episodes(season=season, movie_id=movie_id)
    movie_data = movie_db.get_movie(movie_id=movie_id)
    text = f"🎬 <b>{movie_data['name']}</b>\n"
    
    text += "\n🔻 Filmni ko'rishda davom etish uchun qismni tanlang tanlang!"

    await callback.message.edit_caption(text, reply_markup=episode_watch_keyboard(movie_id, season, episode_data['episodes']))


@dp.callback_query_handler(text_contains="watch_episode", state="*")
async def select_quality(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    movie_id = callback.data.split(":")[1]
    season = callback.data.split(":")[2]
    episode = callback.data.split(":")[3]
    movie_data = movie_db.search_by_episode(season=season, episode=episode, movie_id=movie_id)
    episodes = movie_data['episodes'][0]
    poster_url = movie_data['poster']                         
    caption = f"🎬 <b>{movie_data['name']}</b>\n\n⚪️ <b>{season}</b>-sezon, <b>{episode}</b>-qism: <b>{episodes['name']}</b>\n\n<b>⏰ Davomiylik:</b> {episodes['duration']}\n<b>⭐️ IMDb</b>: {episodes['imdb']}\n<b>📆 Yil</b>: {episodes['year']}\n\n"

    for quality, details in episodes["file_ids"].items():
        size = details['size']
        caption += f"<b>🔰 {quality}</b> — {size} MB\n"

    caption+=f"\n<b>✈️ Kanalimiz:</b> @{OFFICIAL_CHANNEL}\n<b>🤖 Botimiz:</b> @{BOT_HANDLE}"

    await callback.message.edit_caption(caption=caption, reply_markup=choose_quality_episode(movie_id=movie_id, season=season, episode=episode, qualities=episodes["file_ids"].keys()))


@dp.callback_query_handler(text_contains="watch_quality_episode", state="*")
async def watch_movie(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    movie_id = callback.data.split(":")[1]
    season = callback.data.split(":")[2]
    episode = callback.data.split(":")[3]
    quality = callback.data.split(":")[4]
    movie_data = movie_db.search_by_episode(season=season, episode=episode, movie_id=movie_id)
    episode_data = movie_data['episodes'][0]


    file_id = episode_data["file_ids"][quality]["message_id"]
    hajm = episode_data["file_ids"][quality]["size"]
    await callback.message.delete()
    await bot.copy_message(message_id=file_id, 
                           chat_id=callback.from_user.id, 
                           from_chat_id="-1002306588626", 
                           caption=f"🎬 <b>{movie_data['name']}</b>\n\n⚪️ <b>{season}</b>-sezon, <b>{episode}</b>-qism: <b>{episode_data['name']}</b>\n\n<b>🔰 Tanlangan format:</b> {quality}\n<b>⏰ Davomiylik:</b> {episode_data['duration']} min.\n<b>💾 Hajm:</b> {hajm} MB\n\n<b>✈️ Kanalimiz:</b> @{OFFICIAL_CHANNEL}\n<b>🤖 Botimiz:</b> @{BOT_HANDLE}", 
                           reply_markup=back_season_keyboard(movie_id=movie_id, season=season))


@dp.callback_query_handler(text_contains="watch_quality", state="*")
async def watch_movie(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    movie_id = callback.data.split(":")[1]
    quality = callback.data.split(":")[2]
    movie_data = movie_db.get_movie(movie_id=movie_id)
    file_id = movie_data["file_ids"][quality]["message_id"]
    hajm = movie_data["file_ids"][quality]["size"]
    await callback.message.delete()
    await bot.copy_message(message_id=file_id, chat_id=callback.from_user.id, from_chat_id="-1002306588626", caption=f"🎬 <b>{movie_data['name']}</b>\n\n🔰 Tanlangan format: {quality}\n⏰ Davomiylik: {movie_data['duration']} min.\n💾 Hajm: {hajm} MB\n\n<b>✈️ Kanalimiz:</b> @{OFFICIAL_CHANNEL}\n<b>🤖 Botimiz:</b> @{BOT_HANDLE}", reply_markup=back_movie_keyboard(movie_id=movie_id))

@dp.callback_query_handler(text_contains="back_movie", state="*")
async def back_movie(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    movie_id = callback.data.split(":")[1]
    movie_data = movie_db.get_movie(movie_id=movie_id)
    if movie_data is None:
        return
    poster_url = movie_data['poster']
    user_data = ratings_db.get_user_current_status(user_id=callback.from_user.id, movie_id=movie_id)
    zaminfilm = ratings_db.get_rating_movie(movie_id=movie_id)['average_rating'] if ratings_db.get_rating_movie(movie_id=movie_id) is not None else "0"
    views = ratings_db.get_views(movie_id=movie_id)

    if movie_data['type'] == 'movie':
        media = InputMediaPhoto(
            media=poster_url,
            caption=f"🎬 <b>{movie_data['name'].capitalize()}\n\n</b>"
                            f"<b>⭐️ IMDb:</b> {movie_data['imdb']} | KinoPoisk: {movie_data['kinopoisk']} | {BOT_NAME}: {zaminfilm}\n"
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
        )
        await callback.message.edit_media(media=media, reply_markup=movie_details_keyboard(movie_id=movie_id, watchlist=user_data['watchlist'], saved=user_data['saved'], favourite=user_data['favourite'], type="movie"))

    else:
        total_episodes = movie_data['total_episodes']
        total_seasons = movie_data['total_seasons']

        media = InputMediaPhoto(
            media=poster_url,
            caption=f"🎬 <b>{movie_data['name']}</b>\n\n"
                            f"<b>⭐️ IMDb:</b> {movie_data['imdb']} | KinoPoisk: {movie_data['kinopoisk']} | {BOT_NAME}: {zaminfilm}\n"
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
                                f"<b>🤖 Botimiz:</b> @{BOT_HANDLE}",)


        await callback.message.edit_media(media=media, reply_markup=movie_details_keyboard(movie_id=movie_id, watchlist=user_data['watchlist'], saved=user_data['saved'], favourite=user_data['favourite'], type="tv_series"))


@dp.callback_query_handler(text_contains="save_movie", state="*")
async def save_movie(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    movie_id = callback.data.split(":")[1]
    movie_data = movie_db.get_movie(movie_id=movie_id)
    ratings_db.save_movie(user_id=callback.from_user.id, movie_id=movie_id)
    user_data = ratings_db.get_user_current_status(user_id=callback.from_user.id, movie_id=movie_id)
    zaminfilm = ratings_db.get_rating_movie(movie_id=movie_id)['average_rating'] if ratings_db.get_rating_movie(movie_id=movie_id) is not None else "0"
    views = ratings_db.get_views(movie_id=movie_id)

    if movie_data['type'] == 'movie':
        await callback.message.edit_caption(caption=f"🎬 <b>{movie_data['name'].capitalize()}\n\n</b>"
                            f"<b>⭐️ IMDb:</b> {movie_data['imdb']} | KinoPoisk: {movie_data['kinopoisk']} | {BOT_NAME}: {zaminfilm}\n"
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
                                f"<b>🤖 Botimiz:</b> @{BOT_HANDLE}", reply_markup=movie_details_keyboard(movie_id=movie_id, watchlist=user_data['watchlist'], saved=user_data['saved'], favourite=user_data['favourite'], type="movie")

)
    else:
        total_episodes = movie_data['total_episodes']
        total_seasons = movie_data['total_seasons']


        await callback.message.edit_caption(caption=f"🎬 <b>{movie_data['name']}</b>\n\n"
                            f"<b>⭐️ IMDb:</b> {movie_data['imdb']} | KinoPoisk: {movie_data['kinopoisk']} | {BOT_NAME}: {zaminfilm}\n"
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
                                f"<b>🤖 Botimiz:</b> @{BOT_HANDLE}", reply_markup=movie_details_keyboard(movie_id=movie_id, watchlist=user_data['watchlist'], saved=user_data['saved'], favourite=user_data['favourite'], type="tv_series")
)


@dp.callback_query_handler(text_contains="add_to_watchlist", state='*')
async def save_movie(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    movie_id = callback.data.split(":")[1]
    movie_data = movie_db.get_movie(movie_id=movie_id)
    ratings_db.add_to_watchlist(user_id=callback.from_user.id, movie_id=movie_id)
    user_data = ratings_db.get_user_current_status(user_id=callback.from_user.id, movie_id=movie_id)
    zaminfilm = ratings_db.get_rating_movie(movie_id=movie_id)['average_rating'] if ratings_db.get_rating_movie(movie_id=movie_id) is not None else "0"
    views = ratings_db.get_views(movie_id=movie_id)

    if movie_data['type'] == 'movie':
        await callback.message.edit_caption(caption=
                             f"🎬 <b>{movie_data['name'].capitalize()}\n\n</b>"
                             f"<b>⭐️ IMDb:</b> {movie_data['imdb']} | KinoPoisk: {movie_data['kinopoisk']} | {BOT_NAME}: {zaminfilm}\n"
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
                                f"<b>🤖 Botimiz:</b> @{BOT_HANDLE}", reply_markup=movie_details_keyboard(movie_id=movie_id, watchlist=user_data['watchlist'], saved=user_data['saved'], favourite=user_data['favourite'], type="movie")
)
    else:
        total_episodes = movie_data['total_episodes']
        total_seasons = movie_data['total_seasons']


        await callback.message.edit_caption(caption=
                             f"🎬 <b>{movie_data['name']}</b>\n\n"
                             f"<b>⭐️ IMDb:</b> {movie_data['imdb']} | KinoPoisk: {movie_data['kinopoisk']} | {BOT_NAME}: {zaminfilm}\n"
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
                                f"<b>🤖 Botimiz:</b> @{BOT_HANDLE}", reply_markup=movie_details_keyboard(movie_id=movie_id, watchlist=user_data['watchlist'], saved=user_data['saved'], favourite=user_data['favourite'], type="tv_series")
)
        
@dp.callback_query_handler(text_contains="toggle_favourite", state="*")
async def save_movie(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    movie_id = callback.data.split(":")[1]
    movie_data = movie_db.get_movie(movie_id=movie_id)
    ratings_db.toggle_favourite(user_id=callback.from_user.id, movie_id=movie_id)
    user_data = ratings_db.get_user_current_status(user_id=callback.from_user.id, movie_id=movie_id)
    zaminfilm = ratings_db.get_rating_movie(movie_id=movie_id)['average_rating'] if ratings_db.get_rating_movie(movie_id=movie_id) is not None else "0"
    views = ratings_db.get_views(movie_id=movie_id)

    if movie_data['type'] == 'movie':
        await callback.message.edit_caption(caption=f"🎬 <b>{movie_data['name'].capitalize()}\n\n</b>"
                             f"<b>⭐️ IMDb:</b> {movie_data['imdb']} | KinoPoisk: {movie_data['kinopoisk']} | {BOT_NAME}: {zaminfilm}\n"
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
                                f"<b>🤖 Botimiz:</b> @{BOT_HANDLE}", reply_markup=movie_details_keyboard(movie_id=movie_id, watchlist=user_data['watchlist'], saved=user_data['saved'], favourite=user_data['favourite'], type="movie")
)
    else:
        total_episodes = movie_data['total_episodes']
        total_seasons = movie_data['total_seasons']


        await callback.message.edit_caption(caption=f"🎬 <b>{movie_data['name']}</b>\n\n"
                            f"<b>⭐️ IMDb:</b> {movie_data['imdb']} | KinoPoisk: {movie_data['kinopoisk']} | {BOT_NAME}: {zaminfilm}\n"
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
                                f"<b>🤖 Botimiz:</b> @{BOT_HANDLE}", reply_markup=movie_details_keyboard(movie_id=movie_id, watchlist=user_data['watchlist'], saved=user_data['saved'], favourite=user_data['favourite'], type="tv_series")
)



@dp.callback_query_handler(text="favourite_movies", state="*")
async def favourite_movies(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    user_id = callback.from_user.id
    movies = ratings_db.get_favourite_movies(user_id=user_id, limit=10, page=1)

    await callback.message.edit_caption("<b>⭐️ Sevimli kinolaringiz ro'yxati:</b>", reply_markup=movie_list_keyboard(movies=movies, type="favourite"))

@dp.callback_query_handler(text="saved_movies", state="*")
async def saved_movies(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    user_id = callback.from_user.id
    movies = ratings_db.get_saved_movies(user_id=user_id, limit=10, page=1)

    await callback.message.edit_caption("📥 Saqlangan kinolaringiz!", reply_markup=movie_list_keyboard(movies=movies, type='saved'))

@dp.callback_query_handler(text="watchlist_movies", state="*")
async def watchlist_movies(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    user_id = callback.from_user.id
    movies = ratings_db.get_user_watchlist(user_id=user_id, limit=10, page=1)

    await callback.message.edit_caption("🔜 Keyin ko'raman ro'yxatiga qo'shilgan kinolaringiz", reply_markup=movie_list_keyboard(movies=movies, type='watchlist'))    

@dp.callback_query_handler(text_contains='turn_page', state="*")
async def turn_page(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    user_id = callback.from_user.id
    data = callback.data.split(":")
    type = data[1]
    page = int(data[2])
    if type == "favourite":
        movies = ratings_db.get_favourite_movies(user_id=user_id, limit=10, page=page)
    elif type == "saved":
        movies = ratings_db.get_saved_movies(user_id=user_id, limit=10, page=page)
    else:
        movies = ratings_db.get_user_watchlist(user_id=user_id, limit=10, page=page)

    await callback.message.edit_reply_markup(reply_markup=movie_list_keyboard(movies=movies, type=type))
    


@dp.callback_query_handler(text_contains="show_pages", state="*")
async def show_pages(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    user_id = callback.from_user.id
    data = callback.data.split(":")
    type = data[1]
    page = int(data[2])
    if type == "favourite":
        movies = ratings_db.get_favourite_movies(user_id=user_id, limit=10, page=1)
    elif type == "saved":
        movies = ratings_db.get_saved_movies(user_id=user_id, limit=10, page=page)
    else:
        movies = ratings_db.get_user_watchlist(user_id=user_id, limit=10, page=page)


    keyboard = types.InlineKeyboardMarkup(row_width=5)
    for i in range(1, int(movies['total_pages'])+1):
        keyboard.insert(types.InlineKeyboardButton(f"{i}", callback_data=f"turn_page:{type}:{i}"))
    
    keyboard.add(types.InlineKeyboardButton(f"🔙 Ortga", callback_data=f"turn_page:{type}:{page}"))

    await callback.message.edit_caption(caption="📜 Sahifani tanlang! ", reply_markup=keyboard)

    





@dp.callback_query_handler(text="search_by_genre", state="*")
async def search_by_genre(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    genres = genres_db.get_all_genres()
    await callback.message.edit_caption("🎭 Janrlar", reply_markup=display_genres(genres=genres))
    

@dp.callback_query_handler(text_contains="rate_movie", state="*")
async def rate_movie(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    user_id = callback.from_user.id
    movie_id = callback.data.split(":")[1]
    name = movie_db.get_movie(movie_id=movie_id)['name']

    await callback.message.edit_caption(caption=f"🎬 <b>{name}</b> kinosiga bermoqchi bo'lgan bahoyingizni belgilang!\n\n⭐️1-10 dan ballgacha bo'lgan sistemada baholang!", reply_markup=rating_keyboard_builder(movie_id))

@dp.callback_query_handler(text_contains="complete_rating", state="*")
async def rate_movie(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    user_id = callback.from_user.id
    movie_id = callback.data.split(":")[1]
    rating = callback.data.split(":")[2]
    movie_data = movie_db.get_movie(movie_id=movie_id)
    name = movie_data['name']

    res = ratings_db.rate_movie(movie_id=movie_id, user_id=user_id, rating=rating)

    if res == "new":
        await callback.answer(text=f"🎬 {name} kino uchun ⭐️ {rating} baholandi!", show_alert=True)
    else:
        await callback.answer(text=f"🎬 {name} kino uchun ⭐️ {rating} o'tkan safargi bahodan yangilandi!", show_alert=True)

    poster_url = movie_data['poster']
    user_data = ratings_db.get_user_current_status(user_id=callback.from_user.id, movie_id=movie_id)
    zaminfilm = ratings_db.get_rating_movie(movie_id=movie_id)['average_rating'] if ratings_db.get_rating_movie(movie_id=movie_id) is not None else "0"
    views = ratings_db.get_views(movie_id=movie_id)


    if movie_data['type'] == 'movie':
        media = InputMediaPhoto(
            media=poster_url,
            caption=f"🎬 <b>{movie_data['name'].capitalize()}\n\n</b>"
                            f"<b>⭐️ IMDb:</b> {movie_data['imdb']} | KinoPoisk: {movie_data['kinopoisk']} | {BOT_NAME}: {zaminfilm}\n"
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
        )
        await callback.message.edit_media(media=media, reply_markup=movie_details_keyboard(movie_id=movie_id, watchlist=user_data['watchlist'], saved=user_data['saved'], favourite=user_data['favourite'], type="movie"))

    else:
        total_episodes = movie_data['total_episodes']
        total_seasons = movie_data['total_seasons']

        media = InputMediaPhoto(
            media=poster_url,
            caption=f"🎬 <b>{movie_data['name']}</b>\n\n"
                            f"<b>⭐️ IMDb:</b> {movie_data['imdb']} | KinoPoisk: {movie_data['kinopoisk']} | {BOT_NAME}: {zaminfilm}\n"
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
                                f"<b>🤖 Botimiz:</b> @{BOT_HANDLE}",)


        await callback.message.edit_media(media=media, reply_markup=movie_details_keyboard(movie_id=movie_id, watchlist=user_data['watchlist'], saved=user_data['saved'], favourite=user_data['favourite'], type="tv_series"))



@dp.callback_query_handler(text="top_movies", state="*")
async def top_movies(callback: types.CallbackQuery, state: FSMContext):
    top_rated = ratings_db.top_rated()
    final_text = "🔰 Bir necha toifa bo'yicha TOP kinolarni ko'rishingiz mumkin!\n\n"
    final_text += f"⭐️ Eng yaxshi baholangan kinolar({BOT_NAME}):\n"
    count = 0
    key = types.InlineKeyboardMarkup(row_width=5)

    for movie in top_rated:
        movie_details = movie_db.get_movie(movie['movie_id'])
        rating = movie['avg_rating']
        if rating is None:
            rating = 0
        count+=1
        key.insert(types.InlineKeyboardButton(f"{count}", callback_data=f"back_movie:{movie['movie_id']}"))
        final_text+= f"\n{count}. <a href='https://t.me/{BOT_HANDLE}?start=movie_{movie['movie_id']}'>{movie_details['name']} | ⭐️ {rating}</a>"
    final_text += "\n\n👇🏻<i>Bu yerdagi tugmalar orqali boshqa toifa bo'yicha top kinolarni ham topishingiz mumkin</i>"




    key.add(types.InlineKeyboardButton(f"🔝 IMDb", callback_data="filter_top:imdb"))
    key.insert(types.InlineKeyboardButton(f"🔝 KinoPoisk", callback_data="filter_top:kinopoisk"))
    key.insert(types.InlineKeyboardButton(f"✅ {BOT_NAME}", callback_data="filter_top:zaminfilm"))
    key.insert(types.InlineKeyboardButton(f"🔝 Ko'rishlar", callback_data="filter_top:views"))
    key.add(types.InlineKeyboardButton(f"🔙 Ortga", callback_data='back'))

    await callback.message.edit_caption(
        caption=final_text,
        reply_markup=key
    )

@dp.callback_query_handler(text_contains="filter_top", state="*")
async def filter_top(callback: types.CallbackQuery, state: FSMContext):
    filter_type = callback.data.split(":")[1]
    final_text = "🔰 Bir necha toifa bo'yicha TOP kinolarni ko'rishingiz mumkin!\n\n"
    if filter_type == "imdb":
        top = movie_db.top_rating(rating="imdb", limit=5)
        final_text += "🔝 Eng yaxshi baholangan kinolar(IMDb):\n"

    elif filter_type == "kinopoisk":
        top = movie_db.top_rating(rating="kinopoisk", limit=5)
        final_text += "🔝 Eng yaxshi baholangan kinolar(KinoPoisk):\n"

    elif filter_type == "zaminfilm":
        top = ratings_db.top_rated()
        final_text += f"🔝 Eng yaxshi baholangan kinolar({BOT_NAME}):\n"

    else:
        top = ratings_db.top_views()
        final_text += "🔝 Eng ko'p ko'rilgan kinolar:\n"

    count = 0
    key = types.InlineKeyboardMarkup(row_width=5)

    for movie in top:
        movie_details = movie_db.get_movie(movie['movie_id'])
        rating = movie['avg_rating']
        count+=1
        key.insert(types.InlineKeyboardButton(f"{count}", callback_data=f"back_movie:{movie['movie_id']}"))
        final_text+= f"\n{count}. <a href='https://t.me/{BOT_HANDLE}?start=movie_{movie['movie_id']}'>{movie_details['name']} | {'👁' if filter_type == 'views' else '⭐️'} {rating}</a>"
    final_text += "\n\n👇🏻<i>Bu yerdagi tugmalar orqali boshqa toifa bo'yicha top kinolarni ham topishingiz mumkin</i>"




    key.add(types.InlineKeyboardButton(
        f"{'✅' if filter_type == 'imdb' else '🔝'} IMDb", callback_data="filter_top:imdb"
    ),)
    key.insert(types.InlineKeyboardButton(
        f"{'✅' if filter_type == 'kinopoisk' else '🔝'} KinoPoisk", callback_data="filter_top:kinopoisk"
    ),)
    key.insert(types.InlineKeyboardButton(
        f"{'✅' if filter_type == 'zaminfilm' else '🔝'} {BOT_NAME}", callback_data="filter_top:zaminfilm"
    ),)
    key.insert(types.InlineKeyboardButton(
        f"{'✅' if filter_type == 'views' else '🔝'} Ko'rishlar", callback_data="filter_top:views"
    ),)
    key.add(types.InlineKeyboardButton(f"🔙 Ortga", callback_data='back'))

    await callback.message.edit_caption(
        caption=final_text,
        reply_markup=key
    )

    
