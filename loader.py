from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from utils.db_api.sqlite import Database, Channel, MovieDB, RatingsDB, Genres
from pprint import pprint as print
import asyncio
from data import config
import sys


bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
db = Database(path_to_db='data/sqlite/main.db')
channel = Channel(db_name='data/sqlite/channels.db')
movie_db = MovieDB(db_name='data/sqlite/movie.db')
ratings_db = RatingsDB(db_name='data/sqlite/ratings.db')
genres_db = Genres(db_name='data/sqlite/genres.db')




if __name__ == "__main__":
    pass
    # for season in range(4, 10):
    #     episodes_data = {
    #         season: [
    #             {
    #                 "episode": 1,
    #                 "name": "Welcome to the Playground",
    #                 "file_ids": {"480p": {"message_id":"2", "size":769}, "720p": {"message_id":"2", "size":1029}, "1080p": {"message_id":"2", "size":2048}},
    #                 "imdb": 7.1,
    #                 "trailer_url": "trailer_url",
    #                 "duration": 30,
    #                 "year": 2022
    #             },
    #             {
    #                 "episode": 2,
    #                 "name": "Welcome to the Playground",
    #                 "file_ids": {"480p": {"message_id":"2", "size":769}, "720p": {"message_id":"2", "size":1029}, "1080p": {"message_id":"2", "size":2048}},
    #                 "imdb": 7.1,
    #                 "trailer_url": "trailer_url",
    #                 "duration": 30,
    #                 "year": 2022
    #             },
    #         ],

    #     }

    #     movie_db.add_episode(episodes=episodes_data, movie_id=9)
    # for i in range(30, 90):
    movie_db.save_movie(
            id=i,
            name="Arcane",
            size=4096,
            imdb=7.1,
            kinopoisk=7.0,
            genres=["animation", "action"],
            actors=["actor1", "actor2"],
            directors=["director1"],
            detailed_info="A detailed description of Arcane movie.",
            year=2022,
            country="usa",
            duration=107,
            file_ids={"480p": {"message_id":"2", "size":769}, "720p": {"message_id":"2", "size":1029}, "1080p": {"message_id":"2", "size":2048}},
            age_restriction=18,
            trailer_url="youtube_url",
            poster_url="poster_url",
            poster="poster_url",
            nominations=["nom1", "nom2"],
            slogan="Doim olg'a"
        )
    #     ratings_db.toggle_favourite(movie_id=i, user_id=7030976412)

    episodes_data = {
        1: [
            {
                "episode": 1,
                "name": "Welcome to the Playground",
                "file_ids": {"480p": {"message_id":"2", "size":769}, "720p": {"message_id":"2", "size":1029}, "1080p": {"message_id":"2", "size":2048}},
                "imdb": 7.1,
                "trailer_url": "trailer_url",
                "duration": 30,
                "year": 2022
            },
            {
                "episode": 2,
                "name": "Welcome to the Playground",
                "file_ids": {"480p": {"message_id":"2", "size":769}, "720p": {"message_id":"2", "size":1029}, "1080p": {"message_id":"2", "size":2048}},
                "imdb": 7.1,
                "trailer_url": "trailer_url",
                "duration": 30,
                "year": 2022
            },
            {
                "episode": 3,
                "name": "Welcome to the Playground",
                "file_ids": {"480p": {"message_id":"2", "size":769}, "720p": {"message_id":"2", "size":1029}, "1080p": {"message_id":"2", "size":2048}},
                "imdb": 7.1,
                "trailer_url": "trailer_url",
                "duration": 30,
                "year": 2022
            },
            {
                "episode": 4,
                "name": "Welcome to the Playground",
                "file_ids": {"480p": {"message_id":"2", "size":769}, "720p": {"message_id":"2", "size":1029}, "1080p": {"message_id":"2", "size":2048}},
                "imdb": 7.1,
                "trailer_url": "trailer_url",
                "duration": 30,
                "year": 2022
            },
            {
                "episode": 5,
                "name": "Welcome to the Playground",
                "file_ids": {"480p": {"message_id":"2", "size":769}, "720p": {"message_id":"2", "size":1029}, "1080p": {"message_id":"2", "size":2048}},
                "imdb": 7.1,

                "trailer_url": "trailer_url",
                "duration": 30,
                "year": 2022
            },
            {
                "episode": 6,
                "name": "Welcome to the Playground",
                "file_ids": {"480p": {"message_id":"2", "size":769}, "720p": {"message_id":"2", "size":1029}, "1080p": {"message_id":"2", "size":2048}},
                "imdb": 7.1,
                "trailer_url": "trailer_url",
                "duration": 30,
                "year": 2022
            },
        ],
    }


    movie_db.save_tv_series(
        id=5,
        name="Arcane Series",
        size=4096,
        imdb=7.1,
        kinopoisk=7.0,
        genres=["animation", "action"],
        actors=["actor1", "actor2"],
        directors=["director1"],
        detailed_info="Detailed info about the Arcane series.",
        year=2022,
        country="usa",
        duration=108,
        age_restriction=15,
        trailer_url="",
        poster_url="poster_url_series",
        poster="poster_url",
        nominations=[],
        slogan="",
        episodes=episodes_data
    )

    # # 3) Search for movies/TV series (searching in names and episode names)
    # results = movie_db.search_movie("Welcome")
    # print("Search Results:")
    # for result in results:
    #     print(result)

    # # 4) Get movie/TV series details (with pagination for episodes if applicable)
    # movie_details = db.get_movie(movie_id=5, page=1, limit=1)
    # print("\nMovie Details:")
    # print(json.dumps(movie_details, indent=4))

    # # 5) Filter movies by genre (and optionally by name)
    # filtered = db.filter_genres(genre="action", name="Arcane")
    # print("\nFiltered Movies:")
    # for movie in filtered:
    #     print(movie)

    # # 6) Get top-rated movies by IMDb
    # top_movies = db.top_rating(rating="imdb", limit=10)
    # print("\nTop Rated Movies:")
    # for movie in top_movies:
    #     print(movie)
