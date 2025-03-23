from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from loader import movie_db

main = InlineKeyboardMarkup(inline_keyboard=[
	[
		InlineKeyboardButton("🔍 Kino qidirish", callback_data="search_movie"),  
		InlineKeyboardButton("🔝 Top kinolar", callback_data="top_movies"),
              
	],
    [
        InlineKeyboardButton("🔰 Nom orqali qidirish", switch_inline_query_current_chat=""),
        InlineKeyboardButton("🎭 Janrlar orqali qidirish", callback_data="search_by_genre")
	],
	[
		InlineKeyboardButton("⭐️ Sevimli kinolarim", callback_data="favourite_movies"),
		InlineKeyboardButton("📥 Saqlangan kinolar", callback_data="saved_movies"),
	],
    [
    	InlineKeyboardButton("🔜 Keyin ko'raman", callback_data="watchlist_movies"),
	],



])

back = InlineKeyboardMarkup(inline_keyboard=[
	[
		InlineKeyboardButton("🔙 Ortga", callback_data="back")
	]
])

def movie_details_keyboard(movie_id, watchlist, saved, favourite, type):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton("▶️ Ko'rish", callback_data=f"watch_movie:{movie_id}") if type == "movie" else InlineKeyboardButton("▶️ Ko'rish", callback_data=f"watch_tv_series:{movie_id}"),
            InlineKeyboardButton("⭐️ Baholash", callback_data=f"rate_movie:{movie_id}")
            

		],
        [
			InlineKeyboardButton("❌ O'chirish" if saved else "📥 Saqlash" , callback_data=f"save_movie:{movie_id}"),
    		InlineKeyboardButton("✅ Keyin ko'raman" if watchlist else "🔜 Keyin ko'raman", callback_data=f"add_to_watchlist:{movie_id}")
		],
        [
			InlineKeyboardButton("🖤 Sevimlilar ro'yxatidan olish" if favourite else "❤️ Sevimlilar ro'yxatiga qo'shish" , callback_data=f"toggle_favourite:{movie_id}"),
			InlineKeyboardButton("↪️ Ulashish" , switch_inline_query=f"{movie_id}")
            
		],
        [
			InlineKeyboardButton("🔙 Ortga", callback_data="back")
		]
	])
    
    return keyboard

def quality_keyboard(movie_id, qualities):
    keyboard = InlineKeyboardMarkup(row_width=2)
    for quality in qualities:
        keyboard.insert(InlineKeyboardButton(f"🔰 {quality}", callback_data=f"watch_quality:{movie_id}:{quality}"))
    
    keyboard.add(InlineKeyboardButton(text="🔙 Ortga", callback_data=f"back_movie:{movie_id}"))

    
    return keyboard

def episodes_watch_keyboard(movie_id, total_seasons):
    keyboard = InlineKeyboardMarkup(row_width=3)
    for season in range(1, total_seasons+1):
        keyboard.insert(InlineKeyboardButton(text=f"{season}-sezon", callback_data=f"watch_season:{movie_id}:{season}"))

    keyboard.add(InlineKeyboardButton(text="🔙 Ortga", callback_data=f"back_movie:{movie_id}"))
    return keyboard


def episode_watch_keyboard(movie_id, season, episodes):
    keyboard = InlineKeyboardMarkup(row_width=5)
    for episode in episodes:
        keyboard.insert(InlineKeyboardButton(text=f"{episode}-qism", callback_data=f"watch_episode:{movie_id}:{season}:{episode}"))
    keyboard.add(InlineKeyboardButton(text="🔙 Ortga", callback_data=f"watch_tv_series:{movie_id}"))
    
    return keyboard

def choose_quality_episode(movie_id, season, episode, qualities):
    keyboard = InlineKeyboardMarkup(row_width=2)
    for quality in qualities:
        keyboard.insert(InlineKeyboardButton(f"🔰 {quality}", callback_data=f"watch_quality_episode:{movie_id}:{season}:{episode}:{quality}"))
    
    keyboard.add(InlineKeyboardButton(text="🔙 Ortga", callback_data=f"watch_season:{movie_id}:{season}"))

    return keyboard

def back_season_keyboard(movie_id, season):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="🔙 Ortga", callback_data=f"watch_season:{movie_id}:{season}"))
    return keyboard
    
def back_movie_keyboard(movie_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="🔙 Ortga", callback_data=f"back_movie:{movie_id}"))
    return keyboard
    
def movie_list_keyboard(movies, type):
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    for movie in movies['movies']:
        name = movie_db.get_movie(movie_id=movie)['name']
        keyboard.insert(InlineKeyboardButton(text=f"🎬 {name}", callback_data=f'back_movie:{movie}'))
    
    next_page = movies['next_page']
    previous_page = movies['previous_page']
    total_pages = movies['total_pages']
    current_page = movies['current_page']
    pagination_buttons = []
    if previous_page is not None:
        pagination_buttons.append(InlineKeyboardButton(text="⬅️", callback_data=f'turn_page:{type}:{previous_page}'))

    pagination_buttons.append(InlineKeyboardButton(text=f"{current_page}/{total_pages}", callback_data=f"show_pages:{type}:{current_page}"))
    if  next_page is not None:
        pagination_buttons.append(InlineKeyboardButton(text="➡️", callback_data=f'turn_page:{type}:{next_page}'))

    keyboard.row(*pagination_buttons) 
    
    keyboard.add(InlineKeyboardButton("🔙 Ortga", callback_data="back"))
    
    return keyboard
        
def display_genres(genres):
    keyboard = InlineKeyboardMarkup(row_width=3)
    for genre in genres:
        keyboard.insert(InlineKeyboardButton(text=f"{genre}", switch_inline_query_current_chat=f"genre:{genre}"))

    keyboard.add(InlineKeyboardButton("🔙 Ortga", callback_data="back"))
    return keyboard

def rating_keyboard_builder(id):
    keyboard = InlineKeyboardMarkup(row_width=5)
    for rating in range(1, 11):
        keyboard.insert(InlineKeyboardButton(text=f"⭐️ {rating}", callback_data=f"complete_rating:{id}:{rating}"))
    keyboard.add(InlineKeyboardButton(text="🔙 Ortga", callback_data=f"back_movie:{id}"))

    return keyboard
