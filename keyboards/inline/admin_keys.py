import json
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from loader import bot

admin_panel_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="💬 Reklama", callback_data='admin:announcement'),
            InlineKeyboardButton(text="🔐 Majburiy Obuna", callback_data='admin:subscription'),

        ],
        [
            InlineKeyboardButton(text="📊 Statistika", callback_data='admin:statistics'),
            InlineKeyboardButton(text="️⚙️ Kino kommandalari", callback_data='admin:movie_actions'),
        ],
    ],
)

movie_action_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🎬 Kino Yuklash", callback_data='admin:upload_movie'),
            InlineKeyboardButton(text="🗑 Kino o'chirish", callback_data='admin:delete_movie'),
        ],
        [
            InlineKeyboardButton(text="🎬 Kino o'zgartirish", callback_data='admin:edit_movie'),
        ],
        [
            InlineKeyboardButton(text="🕺🏻 Aktyorlar", callback_data='admin:specify_actors'),
            InlineKeyboardButton(text="🕺🏻 Rejissyorlar", callback_data='admin:specify_directors'),
        ],
        [
            InlineKeyboardButton(text="🎭 Janrlar", callback_data='admin:specify_genre'),
        ],
        [
            InlineKeyboardButton(text="🔙 Orqaga", callback_data='admin:back'),
        ]

    ]
)

admin_back_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🔙 Orqaga", callback_data='admin:back'),
        ]
    ],
)

async def channels_list_builder(channels_list):
    keyboard = InlineKeyboardMarkup()
    for channel_data in channels_list:
        channel_info = json.loads(channel_data)
        channel_id = channel_info["id"]
        keyboard.add(InlineKeyboardButton(text=str(channel_id), callback_data=f"admin:channel:{channel_id}"))
    keyboard.add(InlineKeyboardButton(text="➕ Kanal qo‘shish", callback_data="admin:add_channel"))
    keyboard.add(InlineKeyboardButton(text="🔙 Orqaga", callback_data='admin:back'))
    return keyboard


def channel_details_keyboard(channel_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="🗑 Ro‘yxatdan olib tashlash", callback_data=f"admin:delete_channel:{channel_id}"))
    keyboard.add(InlineKeyboardButton(text="🔙 Orqaga", callback_data='admin:back_channels_list'))
    return keyboard


back_channels_list = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🔙 Orqaga", callback_data='admin:back_channels_list')
        ]
    ]
)

advert_type_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton("↪️ Forward", callback_data="admin:advert_type:forward"),
        InlineKeyboardButton("🔀 Oddiy", callback_data="admin:advert_type:simple"),
    ],
    [
         InlineKeyboardButton("🔙 Ortga", callback_data="admin:back")
    ]
])

def edit_movie_details(movie_id):
    key = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton("🎦 Kod", callback_data=f"admin:edit_movie_details:code:{movie_id}"),
            InlineKeyboardButton("🎬 Nom", callback_data=f"admin:edit_movie_details:name:{movie_id}"),
            InlineKeyboardButton("⭐️ IMDb", callback_data=f"admin:edit_movie_details:imdb:{movie_id}"),
            InlineKeyboardButton("⭐️ KinoPoisk", callback_data=f"admin:edit_movie_details:kinopoisk:{movie_id}"),
        ],
        [
            InlineKeyboardButton("📆 Yil", callback_data=f"admin:edit_movie_details:year:{movie_id}"),
            InlineKeyboardButton("🌐 Davlat", callback_data=f"admin:edit_movie_details:country:{movie_id}"),
            InlineKeyboardButton("🎭 Janr", callback_data=f"admin:edit_movie_details:genre:{movie_id}"),
        ],
        [
            InlineKeyboardButton("🛎 Rejissorlar", callback_data=f"admin:edit_movie_details:directors:{movie_id}"),
            InlineKeyboardButton("👨‍🎤 Aktyorlar", callback_data=f"admin:edit_movie_details:actors:{movie_id}"),
            InlineKeyboardButton("ℹ️ Tavsif", callback_data=f"admin:edit_movie_details:description:{movie_id}"),
        ],
        [
            InlineKeyboardButton("🟡 Trailer", callback_data=f"admin:edit_movie_details:trailer:{movie_id}"),
            InlineKeyboardButton("📚 Media", callback_data=f"admin:edit_movie_details:media:{movie_id}"),
        ],
        [
            InlineKeyboardButton("🔙 Ortga", callback_data="admin:back")
        ]
    ])

    return key
