import json
from importlib.resources import contents
from typing import List
import asyncio
from aiogram import types
from aiogram.dispatcher.filters import Text
from data.config import ADMINS, BOT_NAME, BOT_HANDLE, OFFICIAL_CHANNEL
from keyboards.inline.admin_keys import (admin_panel_keyboard, admin_back_keyboard, channels_list_builder, 
                                        channel_details_keyboard, back_channels_list, advert_type_keyboard,
                                         movie_action_keyboard, edit_movie_details)
from loader import dp, channel as channeldb, bot, db, ratings_db
from filters.private_chat_filter import IsPrivate
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import ChatNotFound, BadRequest
from aiogram_media_group import media_group_handler
from aiogram.types import InputMediaDocument, InputMediaPhoto, InputMediaVideo, InputMediaAudio
from aiogram import types
from aiogram.dispatcher import FSMContext
from io import BytesIO
from loader import db, movie_db
from aiogram.types import ReplyKeyboardRemove
from aiogram.types import *
from datetime import datetime
import pytz
import requests

def is_valid_url(url):
    try:
        response = requests.head(url, allow_redirects=True)
        return response.status_code == 200
    except requests.RequestException:
        return False




@dp.message_handler(IsPrivate(), content_types=types.ContentType.ANY, state="*", commands="admin", user_id=ADMINS)
async def admin_panel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("🔑 Assalomu alaykum admin! Admin panelga xush kelibsiz! Pastga tugmalar orqali menuni tanlang!", reply_markup=admin_panel_keyboard)


@dp.callback_query_handler(IsPrivate(), text="admin:back", state="*", user_id=ADMINS)
async def admin_back(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await callback.message.edit_text("🔑 Assalomu alaykum admin! Admin panelga xush kelibsiz! Pastga tugmalar orqali menuni tanlang!", reply_markup=admin_panel_keyboard)
@dp.callback_query_handler(text="admin:subscription", user_id=ADMINS)
async def admin_subscription(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    channels_list = channeldb.get_channels()
    await callback.message.edit_text("🔐 Majburiy obunaga qo‘yilgan kanallar ro‘yxati", 
                                     reply_markup=await channels_list_builder(channels_list))


@dp.callback_query_handler(text="admin:back_channels_list", state="*", user_id=ADMINS)
async def admin_back_channels_list(callback: types.CallbackQuery, state: FSMContext):
    await admin_subscription(callback, state)


@dp.callback_query_handler(text_contains="admin:channel", state="*", user_id=ADMINS)
async def admin_channel(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()

    channel_id = int(callback.data.split("admin:channel:")[1])
    channel_data = None

    for item in channeldb.get_channels():
        item = json.loads(item)
        if channel_id == item.get("id"):
            channel_data = item
            break

    if not channel_data:
        await callback.message.answer("❌ Kanal topilmadi!")
        return

    mode = channel_data["mode"]
    chat = await bot.get_chat(channel_id)
    members_count = await bot.get_chat_members_count(channel_id)
    time = channeldb.get_time_channel(channel_id)

    if mode == "simple":
        invite_link = await bot.export_chat_invite_link(channel_id)
        await callback.message.edit_text(
            f"<b>🔐 Kanal:</b> <a href='{invite_link}'>{chat.title}</a>\n\n"
            f"<b>🔗 Ulangan:</b> {time}\n\n"
            f"<b>👥 Obunachilar:</b> {members_count}",
            reply_markup=channel_details_keyboard(channel_id)
        )

    elif mode == "request":
        request_link = await bot.export_chat_invite_link(channel_id, creates_join_request=True)
        await callback.message.edit_text(
            f"<b>🔐 Kanal:</b> <a href='{request_link}'>So‘rov bilan qo‘shiladigan kanal</a>\n\n"
            f"<b>🔗 Ulangan:</b> {time}",
            reply_markup=channel_details_keyboard(channel_id)
        )


@dp.callback_query_handler(text="admin:add_channel", state="*", user_id=ADMINS)
async def admin_add_channel(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("🔐 Kanal turini tanlang:", reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Oddiy kanal", callback_data="admin:add_simple")],
            [InlineKeyboardButton(text="So‘rov bilan kanal", callback_data="admin:add_request")]
        ]
    ))
    await state.set_state("admin:select_mode")


@dp.callback_query_handler(text_startswith="admin:add_", state="admin:select_mode", user_id=ADMINS)
async def admin_select_mode(callback: types.CallbackQuery, state: FSMContext):
    mode = callback.data.replace("admin:add_", "")
    await state.update_data(mode=mode)

    await callback.message.edit_text("🔗 Kanal ID sini kiriting:", reply_markup=back_channels_list)
    await state.set_state("admin:add_channel")


@dp.message_handler(content_types=types.ContentType.TEXT, state="admin:add_channel", user_id=ADMINS)
async def admin_add_channel_message(message: types.Message, state: FSMContext):
    data = await state.get_data()
    mode = data.get("mode", "simple")

    try:
        channel_id = int(message.text.strip())
        await bot.get_chat(channel_id)  # Kanal mavjudligini tekshirish
    except Exception:
        await message.answer("❌ Xatolik: Noto‘g‘ri kanal ID!")
        return

    channel_data = {"id": channel_id, "mode": mode}

    try:
        channeldb.save_channel(json.dumps(channel_data))
        channels_list = channeldb.get_channels()

        await message.answer("<b>🔐 Kanal muvaffaqiyatli qo‘shildi!</b>", 
                             reply_markup=await channels_list_builder(channels_list))
        await state.finish()
    except Exception as e:
        await message.answer(f"❌ Xatolik yuz berdi: {e}", reply_markup=back_channels_list)


@dp.callback_query_handler(text_contains="admin:delete_channel", state="*", user_id=ADMINS)
async def admin_delete_channel(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    channel_id = int(callback.data.split(":")[2])
    channeldb.del_channel(channel_id)

    channels_list = channeldb.get_channels()
    await callback.message.edit_text("🔐 Kanal ro‘yxatdan olib tashlandi!", 
                                     reply_markup=await channels_list_builder(channels_list))



@dp.callback_query_handler(IsPrivate(), text="admin:announcement", state="*", user_id=ADMINS)
async def admin_announcement(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await callback.message.edit_text("💬 Reklama tarqatish uchun uning turini ko'rsating:", reply_markup=advert_type_keyboard)

@dp.callback_query_handler(IsPrivate(), text_contains="admin:advert_type", state="*", user_id=ADMINS)
async def admin_advert_type(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.finish()
    advert_type = callback.data.split(":")[2]
    if advert_type == "forward":
        await forward_advert(callback.message, state)
    elif advert_type == "simple":
        await simple_advert(callback.message, state)

async def forward_advert(message: types.Message, state: FSMContext):
    await message.answer("💬 Forward qilinishi kerak bo'lgan postni menga yuboring:", reply_markup=admin_back_keyboard)
    await state.set_state("admin:advert_forward")

async def simple_advert(message: types.Message, state: FSMContext):
    await message.answer("💬 Reklamani menga yuboring (Reklama foto, video, audio, dokument yoki tekst bo'lishi mumkin):", reply_markup=admin_back_keyboard)
    await state.set_state("admin:advert_simple")

@dp.message_handler(IsPrivate(), content_types=types.ContentType.ANY, state="admin:advert_forward", user_id=ADMINS)
async def admin_advert_forward(message: types.Message, state: FSMContext):
    await state.finish()
    users = db.select_all_users()
    x = 0
    y = 0
    start = datetime.now(pytz.timezone('Asia/Tashkent'))
    i = await message.answer("🔰 Reklama yuborilmoqda, iltimos biroz kutib turing...")
    await message.answer("📢 Reklama tarqatilmoqda...")
    for user in users:
        try:
            await bot.forward_message(chat_id=user[0], from_chat_id=message.from_user.id, message_id=message.message_id)
            y+=1
        except:
            pass
            x+=1


        await asyncio.sleep(0.1)

    finish = datetime.now(pytz.timezone('Asia/Tashkent'))
    farq = finish - start
    
    await message.answer(f"<b>📣 Reklama yuborildi</b>\n\n"
                         f"✅ Qabul qildi: {y} ta\n"
                         f"❌ Yuborilmadi: {x} ta\n\n"
                         f"<b>⏰ Boshlandi:</b> {start.strftime('%H:%M:%S')}\n"
                         f"<b>⏰ Yakunlandi:</b> {finish.strftime('%H:%M:%S')}\n\n"
                         f"<b>🕓 Umumiy ketgan vaqt:</b> {farq.seconds} soniya", reply_markup=admin_back_keyboard)

@dp.message_handler(IsPrivate(), content_types=types.ContentType.TEXT, state="admin:advert_simple", user_id=ADMINS)
async def admin_advert_simple(message: types.Message, state: FSMContext):
    await state.finish()
    users = db.select_all_users()
    x = 0
    y = 0
    start = datetime.now(pytz.timezone('Asia/Tashkent'))
    i = await message.answer("🔰 Reklama yuborilmoqda, iltimos biroz kutib turing...")
    await message.answer("📢 Reklama tarqatilmoqda...")
    for user in users:
        try:
            await bot.send_message(chat_id=user[0], text=message.text)
            y+=1
        except:
            x+=1
        await asyncio.sleep(0.1)
    finish = datetime.now(pytz.timezone('Asia/Tashkent'))
    farq = finish - start
    
    await message.answer(f"<b>📣 Reklama yuborildi</b>\n\n"
                         f"✅ Qabul qildi: {y} ta\n"
                         f"❌ Yuborilmadi: {x} ta\n\n"
                         f"<b>⏰ Boshlandi:</b> {start.strftime('%H:%M:%S')}\n"
                         f"<b>⏰ Yakunlandi:</b> {finish.strftime('%H:%M:%S')}\n\n"
                         f"<b>🕓 Umumiy ketgan vaqt:</b> {farq.seconds} soniya", reply_markup=admin_back_keyboard)

@dp.message_handler(IsPrivate(), content_types=types.ContentType.ANY, state="admin:advert_simple", user_id=ADMINS)
async def admin_advert_simple(message: types.Message, state: FSMContext):



    users = db.select_all_users()
    x = 0
    y = 0
    start = datetime.now(pytz.timezone('Asia/Tashkent'))
    i = await message.answer("🔰 Reklama yuborilmoqda, iltimos biroz kutib turing...")
    await message.answer("📢 Reklama tarqatilmoqda...")
    for user in users:
        try:
            if message.document:
                await bot.send_document(chat_id=user[0], document=message.document.file_id, caption=message.caption or '')
                
            elif message.photo:
                await bot.send_photo(chat_id=user[0], photo=message.photo[-1].file_id, caption=message.caption or '' )
                
                    
            elif message.video:
                await bot.send_video(chat_id=user[0], video=message.video.file_id, caption=message.caption or '' )

            elif message.audio:
                await bot.send_audio(chat_id=user[0], audio=message.audio.file_id, caption=message.caption or '' )
                
            y+=1
        except Exception as e: 
            x+=1
        await asyncio.sleep(0.1)
    finish = datetime.now(pytz.timezone('Asia/Tashkent'))
    farq = finish - start
    
    await message.answer(f"<b>📣 Reklama yuborildi</b>\n\n"
                         f"✅ Qabul qildi: {y} ta\n"
                         f"❌ Yuborilmadi: {x} ta\n\n"
                         f"<b>⏰ Boshlandi:</b> {start.strftime('%H:%M:%S')}\n"
                         f"<b>⏰ Yakunlandi:</b> {finish.strftime('%H:%M:%S')}\n\n"
                         f"<b>🕓 Umumiy ketgan vaqt:</b> {farq.seconds} soniya", reply_markup=admin_back_keyboard)


@dp.message_handler(IsPrivate(), content_types=types.ContentType.ANY, state="admin:advert_simple", user_id=ADMINS)
@media_group_handler
async def admin_advert_simple(messages: List[types.Message], state: FSMContext):
    await state.finish()
    media_group = []

    if isinstance(messages, list):
        pass
    else:
        messages = [messages]
    for message in messages:
        if message.document:
            media_group.append(
                InputMediaDocument(
                    media=message.document.file_id,
                    caption=message.caption or '' 
                )
            )
        elif message.photo:
            media_group.append(
                InputMediaPhoto(
                    media=message.photo[-1].file_id,
                    caption=message.caption or '' 
                )
            )
        elif message.video:
            media_group.append(
                InputMediaVideo(
                    media=message.video.file_id,
                    caption=message.caption or '' 
                )
            )
        elif message.audio:
            media_group.append(
                InputMediaAudio(
                    media=message.audio.file_id,
                    caption=message.caption or '' 
                )
            )

    users = db.select_all_users()
    x = 0
    y = 0
    start = datetime.now(pytz.timezone('Asia/Tashkent'))
    i = await message.answer("🔰 Reklama yuborilmoqda, iltimos biroz kutib turing...")
    await message.answer("📢 Reklama tarqatilmoqda...")
    for user in users:
        try:
            await bot.send_media_group(chat_id=user[0], media=media_group)
            y+=1
        except:
            x+=1
        await asyncio.sleep(0.1)
    finish = datetime.now(pytz.timezone('Asia/Tashkent'))
    farq = finish - start
    
    await message.answer(f"<b>📣 Reklama yuborildi</b>\n\n"
                         f"✅ Qabul qildi: {y} ta\n"
                         f"❌ Yuborilmadi: {x} ta\n\n"
                         f"<b>⏰ Boshlandi:</b> {start.strftime('%H:%M:%S')}\n"
                         f"<b>⏰ Yakunlandi:</b> {finish.strftime('%H:%M:%S')}\n\n"
                         f"<b>🕓 Umumiy ketgan vaqt:</b> {farq.seconds} soniya", reply_markup=admin_back_keyboard)



@dp.callback_query_handler(state="*", text='admin:statistics')
async def bot_stat(call: types.CallbackQuery, state: FSMContext):
    await call.answer("Kutib turing ...")
    count = db.count_users()[0]
    await call.message.edit_text(f"🤖 Botda jami <b>{count}</b> ta obunachi, aktiv obunachilar malumoti tez orada keladi.", reply_markup=admin_back_keyboard)
    await state.finish()
    users = db.select_all_users()
    x = 0
    y = 0
    for user in users:
        try:
            await bot.get_chat(user[0])
            x += 1
        except:
            y += 1
    await call.message.answer(f"✅ Aktiv: {x}\n"
                      f"❌ Bloklangan: {y}\n"
                      f"➖➖➖➖➖➖\n"
                      f"Umumiy: {count} ta")

@dp.callback_query_handler(state="*", text='admin:upload_movie')
async def upload_movie(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("🎬 Kino yuklash uchun dastavval menga kino IDsini yuboring:", reply_markup=admin_back_keyboard)
    await state.set_state("admin:upload_movie")

@dp.message_handler(state="admin:upload_movie", user_id=ADMINS)
async def upload_movie(message: types.Message, state: FSMContext):
    await state.finish()
    movie_id = message.text
    try:
        int(movie_id)
    except:
        await message.answer("❌ Kino ID raqami faqat raqamlardan iborat bo'lishi kerak! Qaytadan kiriting:", reply_markup=admin_back_keyboard)
        await state.set_state("admin:upload_movie")
        return
    movie = movie_db.get_movie(movie_id=movie_id)
    if movie is not None:
        await message.answer("❌ Bunday kino kodi allaqachon Bazada bor va afsuski men uni qabul qila olmayman! Qaytadan nom kiriting:", reply_markup=admin_back_keyboard)
        await state.set_state("admin:upload_movie")

    else:
        await message.answer("🎬 Kino nomini kiriting:", reply_markup=admin_back_keyboard)
        await state.update_data({"movie_id": movie_id})
        await state.set_state("admin:upload_movie_name")

@dp.message_handler(state="admin:upload_movie_name", user_id=ADMINS)
async def upload_movie_name(message: types.Message, state: FSMContext):
    movie_id = (await state.get_data())["movie_id"]
    await state.finish()
    await message.answer("🎬 Kino videosini hajmini kiriting:", reply_markup=admin_back_keyboard)
    await state.update_data({"movie_id": movie_id, "name": message.text})
    await state.set_state("admin:upload_movie_size")

@dp.message_handler(state="admin:upload_movie_size", user_id=ADMINS)
async def upload_movie_size(message: types.Message, state: FSMContext):
    movie_id = (await state.get_data())["movie_id"]
    name = (await state.get_data())["name"]
    await state.finish()
    await message.answer("🎬 Kinoning IMDb va Kinopoisk reytingini jo'nating(Misol: 7.1/7.2 (Izoh 7.1 IMDB 7.2 KinoPoisk bu yerda)):", reply_markup=admin_back_keyboard)
    await state.update_data({"movie_id": movie_id, "name": name, "size": message.text})
    await state.set_state("admin:upload_movie_rating")

@dp.message_handler(state="admin:upload_movie_rating", user_id=ADMINS)
async def upload_movie_rating(message: types.Message, state: FSMContext):
    movie_id = (await state.get_data())["movie_id"]
    name = (await state.get_data())["name"]
    size = (await state.get_data())["size"]
    imdb = message.text.split("/")[0]
    kp = message.text.split("/")[1]
    await state.finish()
    await message.answer("🎬 Kinoning janr(lar)i kiriting:(Misol: Jangari, Fantastik, Komediya)", reply_markup=admin_back_keyboard)
    await state.update_data({"movie_id": movie_id, "name": name, "size": size, "imdb": imdb, "kp": kp})
    await state.set_state("admin:upload_movie_genre")

@dp.message_handler(state="admin:upload_movie_genre", user_id=ADMINS)
async def upload_movie_genre(message: types.Message, state: FSMContext):
    movie_id = (await state.get_data())["movie_id"]
    name = (await state.get_data())["name"]
    size = (await state.get_data())["size"]
    imdb = (await state.get_data())["imdb"]
    kp = (await state.get_data())["kp"]
    genres = message.text.split(",")
    await state.finish()
    await message.answer("🎬 Kinoni chiqarilgan yilini kiriting:", reply_markup=admin_back_keyboard)
    await state.update_data({"movie_id": movie_id, "name": name, "size": size, "imdb": imdb, "kp": kp, "genres": genres})
    await state.set_state("admin:upload_movie_year")

@dp.message_handler(state="admin:upload_movie_year", user_id=ADMINS)
async def upload_movie_year(message: types.Message, state: FSMContext):
    movie_id = (await state.get_data())["movie_id"]
    name = (await state.get_data())["name"]
    size = (await state.get_data())["size"]
    imdb = (await state.get_data())["imdb"]
    kp = (await state.get_data())["kp"]
    genres = (await state.get_data())["genres"]
    year = message.text
    await state.finish()
    await message.answer("🎬 Kinoning davomiyligini kiriting:", reply_markup=admin_back_keyboard)
    await state.update_data({"movie_id": movie_id, "name": name, "size": size, "imdb": imdb, "kp": kp, "genres": genres, "year": year})
    await state.set_state("admin:upload_movie_duration")

@dp.message_handler(state="admin:upload_movie_duration", user_id=ADMINS)
async def upload_movie_duration(message: types.Message, state: FSMContext):
    movie_id = (await state.get_data())["movie_id"]
    name = (await state.get_data())["name"]
    size = (await state.get_data())["size"]
    imdb = (await state.get_data())["imdb"]
    kp = (await state.get_data())["kp"]
    genres = (await state.get_data())["genres"]
    year = (await state.get_data())["year"]
    duration = message.text
    await state.finish()
    await message.answer("🎬 Kinoni tavsifini kiriting:", reply_markup=admin_back_keyboard)
    await state.update_data({"movie_id": movie_id, "name": name, "size": size, "imdb": imdb, "kp": kp, "genres": genres, "year": year, "duration": duration})
    await state.set_state("admin:upload_movie_description")

@dp.message_handler(state="admin:upload_movie_description", user_id=ADMINS)
async def upload_movie_description(message: types.Message, state: FSMContext):
    movie_id = (await state.get_data())["movie_id"]
    name = (await state.get_data())["name"]
    size = (await state.get_data())["size"]
    imdb = (await state.get_data())["imdb"]
    kp = (await state.get_data())["kp"]
    genres = (await state.get_data())["genres"]
    year = (await state.get_data())["year"]
    duration = (await state.get_data())["duration"]
    description = message.text
    await state.finish()
    await message.answer("🎬 Kinoni aktyorlarini kiriting(Misol: Chris Evans, Tobey Maguire, Harry Maguire):", reply_markup=admin_back_keyboard)
    await state.update_data({"movie_id": movie_id, "name": name, "size": size, "imdb": imdb, "kp": kp, "genres": genres, "year": year, "duration": duration, "description": description})
    await state.set_state("admin:upload_movie_actors")

@dp.message_handler(state="admin:upload_movie_actors", user_id=ADMINS)
async def upload_movie_actors(message: types.Message, state: FSMContext):
    movie_id = (await state.get_data())["movie_id"]
    name = (await state.get_data())["name"]
    size = (await state.get_data())["size"]
    imdb = (await state.get_data())["imdb"]
    kp = (await state.get_data())["kp"]
    genres = (await state.get_data())["genres"]
    year = (await state.get_data())["year"]
    duration = (await state.get_data())["duration"]
    description = (await state.get_data())["description"]
    actors = message.text.split(",")
    await state.finish()
    await message.answer("🎬 Kinoni direktorlarini kiriting(Misol: Christopher Nolan, Stan Lee):", reply_markup=admin_back_keyboard)
    await state.update_data({"movie_id": movie_id, "name": name, "size": size, "imdb": imdb, "kp": kp, "genres": genres, "year": year, "duration": duration, "description": description, "actors": actors})
    await state.set_state("admin:upload_movie_directors")

@dp.message_handler(state="admin:upload_movie_directors", user_id=ADMINS)
async def upload_movie_directors(message: types.Message, state: FSMContext):
    movie_id = (await state.get_data())["movie_id"]
    name = (await state.get_data())["name"]
    size = (await state.get_data())["size"]
    imdb = (await state.get_data())["imdb"]
    kp = (await state.get_data())["kp"]
    genres = (await state.get_data())["genres"]
    year = (await state.get_data())["year"]
    duration = (await state.get_data())["duration"]
    description = (await state.get_data())["description"]
    actors = (await state.get_data())["actors"]
    directors = message.text.split(",")
    await state.finish()
    await message.answer("🎬 Kinoni davlatini kiriting:", reply_markup=admin_back_keyboard)
    await state.update_data({"movie_id": movie_id, "name": name, "size": size, "imdb": imdb, "kp": kp, "genres": genres, "year": year, "duration": duration, "description": description, "actors": actors, "directors": directors})
    await state.set_state("admin:upload_movie_country")

@dp.message_handler(state="admin:upload_movie_country", user_id=ADMINS)
async def upload_movie_country(message: types.Message, state: FSMContext):
    movie_id = (await state.get_data())["movie_id"]
    name = (await state.get_data())["name"]
    size = (await state.get_data())["size"]
    imdb = (await state.get_data())["imdb"]
    kp = (await state.get_data())["kp"]
    genres = (await state.get_data())["genres"]
    year = (await state.get_data())["year"]
    duration = (await state.get_data())["duration"]
    description = (await state.get_data())["description"]
    actors = (await state.get_data())["actors"]
    directors = (await state.get_data())["directors"]
    country = message.text
    await state.finish()
    await message.answer("🎬 Kinoni trailerini yuboring:", reply_markup=admin_back_keyboard)
    await state.update_data({"movie_id": movie_id, "name": name, "size": size, "imdb": imdb, "kp": kp, "genres": genres, "year": year, "duration": duration, "description": description, "actors": actors, "directors": directors, "country": country})
    await state.set_state("admin:upload_movie_trailer")

@dp.message_handler(state="admin:upload_movie_trailer", user_id=ADMINS)
async def upload_movie_trailer(message: types.Message, state: FSMContext):
    movie_id = (await state.get_data())["movie_id"]
    name = (await state.get_data())["name"]
    size = (await state.get_data())["size"]
    imdb = (await state.get_data())["imdb"]
    kp = (await state.get_data())["kp"]
    genres = (await state.get_data())["genres"]
    year = (await state.get_data())["year"]
    duration = (await state.get_data())["duration"]
    description = (await state.get_data())["description"]
    actors = (await state.get_data())["actors"]
    directors = (await state.get_data())["directors"]
    country = (await state.get_data())["country"]
    trailer = message.text
    await state.finish()
    await message.answer("🎬 Kinoni posterini yuboring:", reply_markup=admin_back_keyboard)
    await state.update_data({"movie_id": movie_id, "name": name, "size": size, "imdb": imdb, "kp": kp, "genres": genres, "year": year, "duration": duration, "description": description, "actors": actors, "directors": directors, "country": country, "trailer": trailer})
    await state.set_state("admin:upload_movie_poster")

@dp.message_handler(state="admin:upload_movie_poster", user_id=ADMINS)
async def upload_movie_poster(message: types.Message, state: FSMContext):
    movie_id = (await state.get_data())["movie_id"]
    name = (await state.get_data())["name"]
    size = (await state.get_data())["size"]
    imdb = (await state.get_data())["imdb"]
    kp = (await state.get_data())["kp"]
    genres = (await state.get_data())["genres"]
    year = (await state.get_data())["year"]
    duration = (await state.get_data())["duration"]
    description = (await state.get_data())["description"]
    actors = (await state.get_data())["actors"]
    directors = (await state.get_data())["directors"]
    country = (await state.get_data())["country"]
    trailer = (await state.get_data())["trailer"]
    poster = message.text
    await state.finish()
    await message.answer("🎬 Kinoni formatlari ularning hajmi va message_idsini yuboring.Misol uchun:\n\n480p: 2, 700\n720p: 5, 1200\n1080p: 6, 3600", reply_markup=admin_back_keyboard)
    await state.update_data({"movie_id": movie_id, "name": name, "size": size, "imdb": imdb, "kp": kp, "genres": genres, "year": year, "duration": duration, "description": description, "actors": actors, "directors": directors, "country": country, "trailer": trailer, "poster": poster})
    await state.set_state("admin:upload_movie_formats")

@dp.message_handler(state="admin:upload_movie_formats", user_id=ADMINS)
async def upload_movie_formats(message: types.Message, state: FSMContext):
    movie_id = (await state.get_data())["movie_id"]
    name = (await state.get_data())["name"]
    size = (await state.get_data())["size"]
    imdb = (await state.get_data())["imdb"]
    kp = (await state.get_data())["kp"]
    genres = (await state.get_data())["genres"]
    year = (await state.get_data())["year"]
    duration = (await state.get_data())["duration"]
    description = (await state.get_data())["description"]
    actors = (await state.get_data())["actors"]
    directors = (await state.get_data())["directors"]
    country = (await state.get_data())["country"]
    trailer = (await state.get_data())["trailer"]
    poster = (await state.get_data())["poster"]
    formats = message.text.split("\n")
    file_ids = {}
    for format in formats:
        parts = format.split(":")
        quality = parts[0]
        other = parts[1].split(",")
        try:
            message_id = int(other[0])
            size = int(other[1])
        except:
            await message.answer("❌ Formatlarni noto'g'ri kiritdingiz! Qaytadan urinib ko'ring:", reply_markup=admin_back_keyboard)
            await state.set_data({"movie_id": movie_id, "name": name, "size": size, "imdb": imdb, "kp": kp, "genres": genres, "year": year, "duration": duration, "description": description, "actors": actors, "directors": directors, "country": country, "trailer": trailer, "poster": poster})
            await state.set_state("admin:upload_movie_formats")
            return
        file_ids[quality] = {"message_id": message_id, "size": size}
    await state.finish()
    await message.answer("🎬 Kinoni yuklash boshlandi!")
    movie_db.save_movie(
        id=movie_id, 
        name=name, 
        size=size, 
        imdb=imdb, 
        kinopoisk=kp, 
        genres=genres,
        actors=actors, 
        directors=directors, 
        detailed_info=description, 
        year=year, 
        country=country, 
        duration=duration, 
        file_ids=file_ids,
        age_restriction=0,
        trailer_url=trailer,
        poster_url=poster, 
        poster=poster, 
        nominations=[],
        slogan=""
    )
    await message.answer("🎬 Kino muvaffaqiyatli yuklandi!", reply_markup=admin_back_keyboard)


@dp.callback_query_handler(IsPrivate(), text="admin:delete_movie", state="*", user_id=ADMINS)
async def delete_movie(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await callback.message.edit_text("🎬 Kino ID raqamini kiriting:", reply_markup=admin_back_keyboard)
    await state.set_state("admin:delete_movie")

@dp.message_handler(IsPrivate(), content_types=types.ContentType.TEXT, state="admin:delete_movie", user_id=ADMINS)
async def delete_movie_message(message: types.Message, state: FSMContext):
    movie_id = message.text
    try:
        int(movie_id)
    except:
        await message.answer("❌ Kino ID raqami faqat raqamlardan iborat bo'lishi kerak! Qaytadan kiriting:", reply_markup=admin_back_keyboard)
        await state.set_state("admin:delete_movie")
        return
    movie = movie_db.get_movie(movie_id=movie_id)
    if movie is None:
        await message.answer("❌ Bunday kino bazada topilmadi! Qaytadan kiriting:", reply_markup=admin_back_keyboard)
        await state.set_state("admin:delete_movie")
        return
    movie_db.delete_movie(movie_id=movie_id)
    ratings_db.del_movie(movie_id=movie_id)
    await message.answer("🎬 Kino muvaffaqiyatli o'chirildi!", reply_markup=admin_back_keyboard)
    await state.finish()

@dp.callback_query_handler(IsPrivate(),text='admin:movie_actions', state='*', user_id=ADMINS)
async def specify_movie_actions(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text='🎬 Kino ustida quyidagi amallar mavjud:', reply_markup=movie_action_keyboard)


@dp.callback_query_handler(IsPrivate(), text='admin:edit_movie', state='*', user_id=ADMINS)
async def edit_movie(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("O'zgartirish uchun kino idsini menga yuboring:", reply_markup=admin_back_keyboard)
    await state.set_state("admin:edit_movie")

@dp.message_handler(IsPrivate(), state="admin:edit_movie", user_id=ADMINS)
async def get_movie_id(message: types.Message, state: FSMContext, movie_id = None):
    await state.finish()
    if movie_id is None:
        movie_id = message.text

    movie_data = movie_db.get_movie(movie_id=movie_id)
    if movie_data is None:
        return
    poster_url = movie_data['poster']
    selfrating = ratings_db.get_rating_movie(movie_id=movie_id)['average_rating'] if ratings_db.get_rating_movie(
        movie_id=movie_id) is not None else "0"
    views = ratings_db.get_views(movie_id=movie_id)
    is_valid = is_valid_url(poster_url)
    if is_valid:
        media = poster_url
    else:
        media = False
    if movie_data['type'] == 'movie':
        caption=(f"🎬 <b>{movie_data['name'].capitalize()}\n\n</b>"
                    f"<b>⭐️ IMDb:</b> {movie_data['imdb']} | KinoPoisk: {movie_data['kinopoisk']} | {BOT_NAME}: {selfrating}\n"
                    f"<b>👁 Ko'rishlar soni:</b> {views}\n"
                    f"<b>📆 Yil:</b> {movie_data['year']}\n"
                    f"<b>🌐 Davlat:</b> {movie_data['country'].capitalize()}\n"
                    f"<b>🎭 Janri:</b> {', '.join(genre.title() for genre in movie_data['genres'])}\n"
                    f"<b>🛎 Rejissorlar:</b> {', '.join(director.title() for director in movie_data['directors'])}\n"
                    f"<b>👨‍🎤 Aktyorlar:</b> {', '.join(actor.title() for actor in movie_data['actors'])}\n"
                    f"<b>ℹ️ Tavsif:</b> <blockquote expandable><span class='tg-spoiler'>{movie_data['detailed_info'].capitalize()}</span></blockquote>\n"
                    f"<b>🟡 Trailer:</b> <a href='{movie_data['trailer_url']}'>bu yerga bosing</a>\n"
                    f"➖➖➖➖➖➖➖➖➖➖➖\n"
                    f"<b>✈️ Kanalimiz:</b> @{OFFICIAL_CHANNEL}\n"
                    f"<b>🤖 Botimiz:</b> @{BOT_HANDLE}")

    else:
        total_episodes = movie_data['total_episodes']
        total_seasons = movie_data['total_seasons']

        caption=(f"🎬 <b>{movie_data['name']}</b>\n\n"
                    f"<b>⭐️ IMDb:</b> {movie_data['imdb']} | KinoPoisk: {movie_data['kinopoisk']} | {BOT_NAME}: {selfrating}\n"
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
                    f"<b>✈️ Kanalimiz:</b> {OFFICIAL_CHANNEL}\n"
                    f"<b>🤖 Botimiz:</b> @{BOT_HANDLE}")
    if is_valid:
        await message.answer_photo(media, caption=caption, reply_markup=edit_movie_details(movie_id=movie_id))
    else:
        await message.answer(caption, reply_markup=edit_movie_details(movie_id=movie_id))


@dp.callback_query_handler(IsPrivate(), text_contains='admin:edit_movie_details', state='*', user_id=ADMINS)
async def edit_movie_details_handler(callback: types.CallbackQuery, state: FSMContext):
    edit_type = callback.data.split(":")
    type = edit_type[2]
    movie_id = edit_type[3]
    await state.update_data({"movie_id": movie_id, "type": type})
    if type == "code":
        await callback.message.delete()
        await callback.message.answer('Kino uchun yangi kodni kiriting:', reply_markup=admin_back_keyboard)
        await state.set_state('edit_movie_code')
    elif type == "name":
        await callback.message.delete()
        await callback.message.answer('Kino uchun yangi ismni kiriting:', reply_markup=admin_back_keyboard)
        await state.set_state('edit_movie_name')
    elif type == "year":
        await callback.message.delete()
        await callback.message.answer('Kino uchun yangi yilni kiriting:', reply_markup=admin_back_keyboard)
        await state.set_state('edit_movie_year')
    elif type == "country":
        await callback.message.delete()
        await callback.message.answer('Kino uchun yangi davlatni kiriting:', reply_markup=admin_back_keyboard)
        await state.set_state('edit_movie_country')
    elif type == "description":
        await callback.message.delete()
        await callback.message.answer('Kino uchun yangi tavsifni kiriting:', reply_markup=admin_back_keyboard)
        await state.set_state('edit_movie_description')
    elif type == "trailer":
        await callback.message.delete()
        await  callback.message.answer('Kino uchun yangi trailerni kiriting:', reply_markup=admin_back_keyboard)
        await state.set_state('edit_movie_trailer')
    elif type == "poster":
        await callback.message.delete()
        await  callback.message.answer('Kino uchun yangi posterni kiriting:', reply_markup=admin_back_keyboard)
        await state.set_state('edit_movie_poster')
    elif type == "media":
        await callback.message.delete()
        await  callback.message.answer('Kino uchun yangi medialar ni kiriting:', reply_markup=admin_back_keyboard)
        await state.set_state('edit_movie_media')
    elif type == 'imdb':
        await callback.message.delete()
        await callback.message.answer('Kino uchun yangi imdb reyting ni kiriting:', reply_markup=admin_back_keyboard)
        await state.set_state('edit_movie_imdb')
    elif type == 'kinopoisk':
        await callback.message.delete()
        await callback.message.answer('Kino uchun yangi kinopoisk reyting ni kiriting:', reply_markup=admin_back_keyboard)
        await state.set_state('edit_movie_kinopoisk')
    elif type == 'duration':
        await callback.message.delete()
        await callback.message.answer('Kino uchun yangi qiymatni kiriting:', reply_markup=admin_back_keyboard)
        await state.set_state('edit_movie_duration')
    elif type == 'genres':
        await callback.message.delete()
        await callback.message.answer('Kino uchun yangi jannrlarni kiriting:', reply_markup=admin_back_keyboard)
        await state.set_state('edit_movie_genres')
    elif type == 'actors':
        await callback.message.delete()
        await  callback.message.answer('Kino uchun yangi aktyorlarni kiriting:', reply_markup=admin_back_keyboard)
        await state.set_state('edit_movie_actors')
    elif type == 'directors':
        await callback.message.delete()
        await callback.message.answer('Kino uchun yangi rejissorlarni kiriting:', reply_markup=admin_back_keyboard)
        await state.set_state('edit_movie_directors')
    elif type == 'age_restriction':
        await callback.message.delete()
        await callback.message.answer('Kino uchun yangi yoshni kiriting:', reply_markup=admin_back_keyboard)
        await state.set_state('edit_movie_age_restriction')


@dp.message_handler(IsPrivate(), state="edit_movie_code", user_id=ADMINS)
async def edit_movie_code(message: types.Message, state: FSMContext):
    movie_id = (await state.get_data())["movie_id"]
    new_movie_id = message.text
    try:
        int(new_movie_id)
    except:    
        await message.answer("❌ Kino ID raqami faqat raqamlardan iborat bo'lishi kerak! Qaytadan kiriting:", reply_markup=admin_back_keyboard)
        await state.update_data({"movie_id": movie_id, "type": type})
        await state.set_state("edit_movie_code")
        return
    movie_db.edit_info(movie_id=movie_id, new_movie_id=new_movie_id)
    await get_movie_id(message, state, movie_id=new_movie_id)


@dp.message_handler(IsPrivate(), state="edit_movie_name", user_id=ADMINS)
async def edit_movie_name(message: types.Message, state: FSMContext):
    movie_id = (await state.get_data())["movie_id"]
    new_name = message.text
    movie_db.edit_info(movie_id=movie_id, name=new_name)
    await get_movie_id(message, state, movie_id=movie_id)



@dp.message_handler(IsPrivate(), state="edit_movie_year", user_id=ADMINS)
async def edit_movie_year(message: types.Message, state: FSMContext):
    movie_id = (await state.get_data())["movie_id"]
    new_year = message.text
    movie_db.edit_info(movie_id=movie_id, year=new_year)
    await get_movie_id(message, state, movie_id=movie_id)


@dp.message_handler(IsPrivate(), state="edit_movie_country", user_id=ADMINS)
async def edit_movie_country(message: types.Message, state: FSMContext):
    movie_id = (await state.get_data())["movie_id"]
    new_country = message.text
    movie_db.edit_info(movie_id=movie_id, country=new_country)
    await get_movie_id(message, state, movie_id=movie_id)

@dp.message_handler(IsPrivate(), state="edit_movie_description", user_id=ADMINS)
async def edit_movie_description(message: types.Message, state: FSMContext):
    movie_id = (await state.get_data())["movie_id"]
    new_description = message.text
    movie_db.edit_info(movie_id=movie_id, detailed_info=new_description)
    await get_movie_id(message, state, movie_id=movie_id)

@dp.message_handler(IsPrivate(), state="edit_movie_trailer", user_id=ADMINS)
async def edit_movie_trailer(message: types.Message, state: FSMContext):
    movie_id = (await state.get_data())["movie_id"]
    new_trailer = message.text
    movie_db.edit_info(movie_id=movie_id, trailer_url=new_trailer)
    await get_movie_id(message, state, movie_id=movie_id)

@dp.message_handler(IsPrivate(), state="edit_movie_poster", user_id=ADMINS)
async def edit_movie_poster(message: types.Message, state: FSMContext):
    movie_id = (await state.get_data())["movie_id"]
    new_poster = message.text
    movie_db.edit_info(movie_id=movie_id, poster_url=new_poster)
    await get_movie_id(message, state, movie_id=movie_id)

@dp.message_handler(IsPrivate(), state="edit_movie_media", user_id=ADMINS)
async def edit_movie_media(message: types.Message, state: FSMContext):
    movie_id = (await state.get_data())["movie_id"]
    formats = message.text.split("\n")
    file_ids = {}
    for format in formats:
        parts = format.split(":")
        quality = parts[0]
        other = parts[1].split(",")
        try:
            message_id = int(other[0])
            size = int(other[1])
        except:
            await message.answer("❌ Formatlarni noto'g'ri kiritdingiz! Qaytadan urinib ko'ring:", reply_markup=admin_back_keyboard)
            return
        file_ids[quality] = {"message_id": message_id, "size": size}
    movie_db.edit_info(movie_id=movie_id, file_ids=file_ids)
    await get_movie_id(message, state, movie_id=movie_id)

@dp.message_handler(IsPrivate(), state="edit_movie_imdb", user_id=ADMINS)
async def edit_movie_imdb(message: types.Message, state: FSMContext):
    movie_id = (await state.get_data())["movie_id"]
    new_imdb = message.text
    movie_db.edit_info(movie_id=movie_id, imdb=new_imdb)
    await get_movie_id(message, state, movie_id=movie_id)

@dp.message_handler(IsPrivate(), state="edit_movie_kinopoisk", user_id=ADMINS)
async def edit_movie_kinopoisk(message: types.Message, state: FSMContext):
    movie_id = (await state.get_data())["movie_id"]
    new_kinopoisk = message.text
    movie_db.edit_info(movie_id=movie_id, kinopoisk=new_kinopoisk)
    await get_movie_id(message, state, movie_id=movie_id)

@dp.message_handler(IsPrivate(), state="edit_movie_duration", user_id=ADMINS)
async def edit_movie_duration(message: types.Message, state: FSMContext):
    movie_id = (await state.get_data())["movie_id"]
    new_duration = message.text
    movie_db.edit_info(movie_id=movie_id, duration=new_duration)
    await get_movie_id(message, state, movie_id=movie_id)

@dp.message_handler(IsPrivate(), state="edit_movie_genres", user_id=ADMINS)
async def edit_movie_genres(message: types.Message, state: FSMContext):
    movie_id = (await state.get_data())["movie_id"]
    new_genres = message.text.split(",")
    movie_db.edit_info(movie_id=movie_id, genres=new_genres)
    await get_movie_id(message, state, movie_id=movie_id)

@dp.message_handler(IsPrivate(), state="edit_movie_actors", user_id=ADMINS)
async def edit_movie_actors(message: types.Message, state: FSMContext):
    movie_id = (await state.get_data())["movie_id"]
    new_actors = message.text.split(",")
    movie_db.edit_info(movie_id=movie_id, actors=new_actors)
    await get_movie_id(message, state, movie_id=movie_id)

@dp.message_handler(IsPrivate(), state="edit_movie_directors", user_id=ADMINS)
async def edit_movie_directors(message: types.Message, state: FSMContext):
    movie_id = (await state.get_data())["movie_id"]
    new_directors = message.text.split(",")
    movie_db.edit_info(movie_id=movie_id, directors=new_directors)
    await get_movie_id(message, state, movie_id=movie_id)

@dp.message_handler(IsPrivate(), state="edit_movie_age_restriction", user_id=ADMINS)
async def edit_movie_age_restriction(message: types.Message, state: FSMContext):
    movie_id = (await state.get_data())["movie_id"]
    new_age_restriction = message.text
    movie_db.edit_info(movie_id=movie_id, age_restriction=new_age_restriction)
    await get_movie_id(message, state, movie_id=movie_id)


