import sqlite3
from datetime import datetime
from fuzzywuzzy import fuzz
import json


class Database:
    def __init__(self, path_to_db="main.db"):
        self.path_to_db = path_to_db

    @property
    def connection(self):
        return sqlite3.connect(self.path_to_db)

    def execute(self, sql: str, parameters: tuple = None, fetchone=False, fetchall=False, commit=False):
        if not parameters:
            parameters = ()
        connection = self.connection
        cursor = connection.cursor()
        data = None
        cursor.execute(sql, parameters)

        if commit:
            connection.commit()
        if fetchall:
            data = cursor.fetchall()
        if fetchone:
            data = cursor.fetchone()
        connection.close()
        return data

    def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Users (
            id int NOT NULL,
            fullname varchar(255) NOT NULL,
            username varchar(255),
            PRIMARY KEY (id)
            );
"""
        self.execute(sql, commit=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ?" for item in parameters
        ])
        return sql, tuple(parameters.values())

    def add_user(self, id: int, fullname: str, username="Lomonosov"):
        sql = """
        INSERT INTO Users(id, fullname, username) VALUES(?, ?, ?)
        """
        self.execute(sql, parameters=(id, fullname, username), commit=True)

    def select_all_users(self):
        sql = """
        SELECT * FROM Users
        """
        return self.execute(sql, fetchall=True)

    def select_user(self, **kwargs):
        sql = "SELECT * FROM Users WHERE "
        sql, parameters = self.format_args(sql, kwargs)

        return self.execute(sql, parameters=parameters, fetchone=True)

    def count_users(self):
        return self.execute("SELECT COUNT(*) FROM Users;", fetchone=True)

    def delete_users(self):
        self.execute("DELETE FROM Users WHERE TRUE", commit=True)


class Channel:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS channels
                                (username TEXT PRIMARY KEY,
                                 saved_time TEXT)''')
        self.conn.commit()

    def save_channel(self, username):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("INSERT INTO channels VALUES (?, ?)", (username, current_time))
        self.conn.commit()

    def get_channels(self):
        self.cursor.execute("SELECT username FROM channels")
        return [row[0] for row in self.cursor.fetchall()]

    def get_time_channel(self, username):
        self.cursor.execute("SELECT saved_time FROM channels WHERE username=?", (username,))
        return result[0] if (result := self.cursor.fetchone()) else None

    def del_channel(self, username):
        self.cursor.execute("SELECT username FROM channels WHERE username=?", (username,))
        if result := self.cursor.fetchone():
            self.cursor.execute("DELETE FROM channels WHERE username=?", (username,))
            self.conn.commit()
            return True
        else:
            return False
        

    def del_channels(self):
        self.cursor.execute("DELETE FROM channels")
        self.conn.commit()

    def __del__(self):
        self.cursor.close()
        self.conn.close()


class MovieDB:
    def __init__(self, db_name="movies.db"):
        self.conn = sqlite3.connect(db_name)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        c = self.conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                size INTEGER,
                imdb REAL,
                kinopoisk REAL,
                genres TEXT,    
                actors TEXT,     
                directors TEXT,  
                detailed_info TEXT,
                year INTEGER,
                country TEXT,
                duration INTEGER,
                file_ids TEXT,     
                age_restriction INTEGER,
                trailer_url TEXT,
                poster_url TEXT,
                nominations TEXT,    
                slogan TEXT,
                poster TEXT
                
            )
        ''')
        
        c.execute('''
                CREATE TABLE IF NOT EXISTS episodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    movie_id INTEGER,   
                    season INTEGER,
                    episode INTEGER,
                    name TEXT,
                    file_ids TEXT,
                    imdb REAL,
                    trailer_url TEXT,
                    duration INTEGER,
                    year INTEGER,
                    UNIQUE(movie_id, season, episode),
                    FOREIGN KEY(movie_id) REFERENCES movies(id)
                )
            ''')
        self.conn.commit()
        self.conn.commit()

    def edit_info(self, movie_id, **kwargs):
        c = self.conn.cursor()
        
        allowed_fields = {"new_movie_id", "name", "size", "imdb", "kinopoisk", "genres", "actors", "directors", 
                          "detailed_info", "year", "country", "duration", "file_ids", "age_restriction", 
                          "trailer_url", "poster_url", "nominations", "slogan", "poster"}
        
        updates = []
        values = []
        
        for key, value in kwargs.items():
                    
            if "new_movie_id" in kwargs:
                updates.append("id = ?")
                values.append(kwargs["new_movie_id"])

            elif key in allowed_fields:
                updates.append(f"{key} = ?")
                if isinstance(value, (list, dict)):
                    values.append(json.dumps(value))
                else:
                    values.append(value)
                    
        if not updates:
            return False 
        
        values.append(movie_id)
        query = f"UPDATE movies SET {', '.join(updates)} WHERE id = ?"
        c.execute(query, values)
        self.conn.commit()
        return True
    
    def save_movie(self, id, name, size, imdb, kinopoisk, genres, actors, directors,
                   detailed_info, year, country, duration, file_ids, age_restriction,
                   trailer_url, poster_url, nominations, slogan, poster):
        c = self.conn.cursor()
        c.execute('''
            INSERT OR REPLACE INTO movies (
                id, name, type, size, imdb, kinopoisk, genres, actors, directors,
                detailed_info, year, country, duration, file_ids, age_restriction,
                trailer_url, poster_url, nominations, slogan, poster
            )
            VALUES (?, ?, 'movie', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            id, name, size, imdb, kinopoisk, json.dumps(genres), json.dumps(actors),
            json.dumps(directors), detailed_info, year, country, duration,
            json.dumps(file_ids), age_restriction, trailer_url, poster_url,
            json.dumps(nominations), slogan, poster
        ))
        self.conn.commit()

    def save_tv_series(self, id, name, size, imdb, kinopoisk, genres, actors, directors,
                       detailed_info, year, country, duration, age_restriction,
                       trailer_url, poster_url, nominations, slogan, episodes, poster):

        c = self.conn.cursor()
        c.execute('''
            INSERT OR REPLACE INTO movies (
                id, name, type, size, imdb, kinopoisk, genres, actors, directors,
                detailed_info, year, country, duration, file_ids, age_restriction,
                trailer_url, poster_url, nominations, slogan, poster
            )
            VALUES (?, ?, 'tv series', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            id, name, size, imdb, kinopoisk, json.dumps(genres), json.dumps(actors),
            json.dumps(directors), detailed_info, year, country, duration,
            json.dumps({}),
            age_restriction, trailer_url, poster_url, json.dumps(nominations), slogan, poster
        ))
        for season, episode_list in episodes.items():
            for ep in episode_list:
                c.execute('''
                    INSERT INTO episodes (
                        movie_id, season, episode, name, file_ids, imdb, trailer_url, duration, year
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    id, season, ep.get("episode"), ep.get("name"),
                    json.dumps(ep.get("file_ids")), ep.get("imdb"),
                    ep.get("trailer_url"), ep.get("duration"), ep.get("year")
                ))
        self.conn.commit()

    def search_movie(self, query):
        c = self.conn.cursor()
        results = {}  
        c.execute('''
                SELECT id as movie_id, name, poster_url, size, year, country, duration, genres, type 
                FROM movies
                WHERE id = ?
        ''', (query,))
        movie = c.fetchone()

        if movie:
            return [dict(movie)]

        pattern = f"%{query}%"
        
        c.execute('''
            SELECT id as movie_id, name, poster_url, size, year, country, duration, genres, type 
            FROM movies
            WHERE name LIKE ?
        ''', (pattern,))
        movies_by_name = c.fetchall()
        for movie in movies_by_name:
            results[movie["movie_id"]] = dict(movie)
        
        c.execute('''
            SELECT DISTINCT m.id as movie_id, m.name, m.poster_url, m.size, m.year, m.country, m.duration, m.genres, m.type
            FROM movies m
            JOIN episodes e ON m.id = e.movie_id
            WHERE e.name LIKE ?
        ''', (pattern,))
        movies_by_episode = c.fetchall()
        for movie in movies_by_episode:
            results[movie["movie_id"]] = dict(movie)
        
        return list(results.values())

    def get_movie(self, movie_id):
        c = self.conn.cursor()
        c.execute('SELECT * FROM movies WHERE id = ?', (movie_id,))
        movie = c.fetchone()
        if not movie:
            return None

        movie_data = dict(movie)
        movie_data["genres"] = json.loads(movie_data["genres"]) if movie_data["genres"] else []
        movie_data["actors"] = json.loads(movie_data["actors"]) if movie_data["actors"] else []
        movie_data["directors"] = json.loads(movie_data["directors"]) if movie_data["directors"] else []
        movie_data["nominations"] = json.loads(movie_data["nominations"]) if movie_data["nominations"] else []
        movie_data["file_ids"] = json.loads(movie_data["file_ids"]) if movie_data["file_ids"] else {}

        if movie_data["type"] == "tv series":
            total_seasons = c.execute('SELECT MAX(season) as total_seasons FROM episodes WHERE movie_id = ?', (movie_id,)).fetchone()["total_seasons"] or 0
            total_episodes = c.execute('SELECT COUNT(*) as total_episodes FROM episodes WHERE movie_id = ?', (movie_id,)).fetchone()["total_episodes"] or 0
            movie_data["total_seasons"] = total_seasons
            movie_data["total_episodes"] = total_episodes

        return movie_data
    def add_episode(self, episodes, movie_id):
        c = self.conn.cursor()
        
        for season, episode_list in episodes.items():
            for ep in episode_list:
                c.execute('''
                    INSERT INTO episodes (
                        movie_id, season, episode, name, file_ids, imdb, trailer_url, duration, year
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    movie_id, season, ep.get("episode"), ep.get("name"),
                    json.dumps(ep.get("file_ids")), ep.get("imdb"),
                    ep.get("trailer_url"), ep.get("duration"), ep.get("year")
                ))
        self.conn.commit()


    def get_episodes(self, movie_id, season):
        c = self.conn.cursor()
        c.execute('''
            SELECT * FROM episodes
            WHERE movie_id = ? AND season = ?
            ORDER BY episode
        ''', (movie_id, season))
        
        episodes = c.fetchall()
        
        episodes_data = []
        episodes_numbers = []

        for ep in episodes:
            ep_data = dict(ep)
            ep_data["file_ids"] = json.loads(ep_data["file_ids"]) if ep_data["file_ids"] else {}
            episodes_data.append(ep_data)
            episodes_numbers.append(ep_data["episode"])

        return {
            "episodes_data": episodes_data,
            "episodes": episodes_numbers
        }



    def delete_movie(self, movie_id):
        c = self.conn.cursor()
        c.execute('SELECT type FROM movies WHERE id = ?', (movie_id,))
        row = c.fetchone()
        if not row:
            return False

        movie_type = row["type"]
        if movie_type == "tv series":
            c.execute('DELETE FROM episodes WHERE movie_id = ?', (movie_id,))
        c.execute('DELETE FROM movies WHERE id = ?', (movie_id,))
        self.conn.commit()
        return True

    def filter_genres(self, genre, name=None):
        c = self.conn.cursor()
        results = {}
        genre_pattern = f"%{genre}%"
        
        if name:
            name_pattern = f"%{name}%"
            
            c.execute('''
                SELECT id as movie_id, name, poster_url, size, year, country, duration, genres, type 
                FROM movies 
                WHERE genres LIKE ? AND name LIKE ?
            ''', (genre_pattern, name_pattern))
            movies_by_name = c.fetchall()
            for movie in movies_by_name:
                results[movie["movie_id"]] = dict(movie)
            
            c.execute('''
                SELECT DISTINCT m.id as movie_id, m.name, m.poster_url, m.size, m.year, m.country, m.duration, m.genres, m.type
                FROM movies m
                JOIN episodes e ON m.id = e.movie_id
                WHERE m.genres LIKE ? AND e.name LIKE ?
            ''', (genre_pattern, name_pattern))
            movies_by_episode = c.fetchall()
            for movie in movies_by_episode:
                results[movie["movie_id"]] = dict(movie)
        else:
            c.execute('''
                SELECT id as movie_id, name, poster_url, size, year, country, duration, genres, type 
                FROM movies 
                WHERE genres LIKE ?
            ''', (genre_pattern,))
            movies_by_genre = c.fetchall()
            for movie in movies_by_genre:
                results[movie["movie_id"]] = dict(movie)
        
        return list(results.values())


    def top_rating(self, rating="imdb", limit=10):
        if rating not in ("imdb", "kinopoisk"):
            raise ValueError("Rating must be either 'imdb' or 'kinopoisk'")

        c = self.conn.cursor()

        query = f"""
        SELECT *
        FROM movies
        ORDER BY
            CASE WHEN {rating} GLOB '-?[0-9]*\.?[0-9]*' THEN CAST({rating} AS REAL) ELSE NULL END DESC,
            CASE WHEN {rating} GLOB '-?[0-9]*\.?[0-9]*' THEN 0 ELSE 1 END,
            {rating} ASC
        LIMIT ?
        """

        c.execute(query, (limit,))
        rows = c.fetchall()

        results = []
        for row in rows:
            movie_data = dict(row)
            movie_data["genres"] = json.loads(movie_data["genres"]) if movie_data["genres"] else []

            movie_data["movie_id"] = movie_data.pop("id")
            movie_data["avg_rating"] = movie_data.get(rating, 0)

            results.append(movie_data)

        return results
    def search_by_episode(self, movie_id, season, episode):
        c = self.conn.cursor()
        c.execute('''
            SELECT * FROM episodes
            WHERE movie_id = ? AND season = ? AND episode = ?
        ''', (movie_id, season, episode))
        
        episode_data = c.fetchone()
        if not episode_data:
            return None 
        
        episode_data = dict(episode_data)
        episode_data["file_ids"] = json.loads(episode_data["file_ids"]) if episode_data["file_ids"] else {}

        c.execute('SELECT * FROM movies WHERE id = ?', (movie_id,))
        movie = c.fetchone()
        if not movie:
            return None
        
        movie_data = dict(movie)
        movie_data["genres"] = json.loads(movie_data["genres"]) if movie_data["genres"] else []
        movie_data["actors"] = json.loads(movie_data["actors"]) if movie_data["actors"] else []
        movie_data["directors"] = json.loads(movie_data["directors"]) if movie_data["directors"] else []
        movie_data["nominations"] = json.loads(movie_data["nominations"]) if movie_data["nominations"] else []
        movie_data["file_ids"] = json.loads(movie_data["file_ids"]) if movie_data["file_ids"] else {}

        movie_data["episodes"] = [episode_data]
        
        return movie_data
    
    
class RatingsDB:
    def __init__(self, db_name="ratings.db"):
        self.conn = sqlite3.connect(db_name)
        self.conn.row_factory = sqlite3.Row 
        self.create_tables()

    def create_tables(self):
        c = self.conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                movie_id INTEGER,
                user_id INTEGER,
                rating REAL,
                UNIQUE(movie_id, user_id), 
                FOREIGN KEY(movie_id) REFERENCES movies(id)
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS saved_movies (
                user_id INTEGER,
                movie_id INTEGER,
                PRIMARY KEY (user_id, movie_id),
                FOREIGN KEY(movie_id) REFERENCES movies(id)
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS views (
                user_id INTEGER,
                movie_id INTEGER,
                PRIMARY KEY (user_id, movie_id),
                FOREIGN KEY(movie_id) REFERENCES movies(id)
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS favourite_movies (
                user_id INTEGER,
                movie_id INTEGER,
                PRIMARY KEY (user_id, movie_id),
                FOREIGN KEY(movie_id) REFERENCES movies(id)
            )
        ''')
        # New table for watchlist
        c.execute('''
            CREATE TABLE IF NOT EXISTS watchlist (
                user_id INTEGER,
                movie_id INTEGER,
                PRIMARY KEY (user_id, movie_id),
                FOREIGN KEY(movie_id) REFERENCES movies(id)
            )
        ''')
        self.conn.commit()

    def rate_movie(self, movie_id, user_id, rating):

        c = self.conn.cursor()

        c.execute('SELECT id FROM ratings WHERE movie_id = ? AND user_id = ?', (movie_id, user_id))
        existing_rating = c.fetchone()

        if existing_rating:
            c.execute('UPDATE ratings SET rating = ? WHERE movie_id = ? AND user_id = ?', (rating, movie_id, user_id))
            self.conn.commit()
            return "updated"
        else:
            c.execute('INSERT INTO ratings (movie_id, user_id, rating) VALUES (?, ?, ?)', (movie_id, user_id, rating))
            self.conn.commit()
            return "new"



    def get_rating_movie(self, movie_id):
        """
        Returns the average rating of a movie (total rating / total users who rated).
        """
        c = self.conn.cursor()
        c.execute('''
            SELECT AVG(rating) AS average_rating, COUNT(*) AS total_ratings
            FROM ratings
            WHERE movie_id = ?
        ''', (movie_id,))
        result = c.fetchone()
        if result:
            return {"average_rating": result["average_rating"], "total_ratings": result["total_ratings"]}
        return {"average_rating": None, "total_ratings": 0}

    def save_movie(self, user_id, movie_id):
        """
        Toggles the saved status for a movie for a user.
        If the movie is already saved, it will be removed.
        """
        c = self.conn.cursor()
        c.execute('''
            SELECT * FROM saved_movies
            WHERE user_id = ? AND movie_id = ?
        ''', (user_id, movie_id))
        existing = c.fetchone()
        if existing:
            # Already saved; remove it.
            c.execute('''
                DELETE FROM saved_movies
                WHERE user_id = ? AND movie_id = ?
            ''', (user_id, movie_id))
        else:
            c.execute('''
                INSERT INTO saved_movies (user_id, movie_id)
                VALUES (?, ?)
            ''', (user_id, movie_id))
        self.conn.commit()

    def update_views(self, movie_id, user_id):
        """
        Updates the view count for a movie. If the user has already viewed, does nothing.
        """
        c = self.conn.cursor()
        c.execute('''
            INSERT OR IGNORE INTO views (user_id, movie_id)
            VALUES (?, ?)
        ''', (user_id, movie_id))
        self.conn.commit()

    def get_views(self, movie_id):
        """
        Returns the total number of views for a movie.
        """
        c = self.conn.cursor()
        c.execute('''
            SELECT COUNT(*) AS total_views
            FROM views
            WHERE movie_id = ?
        ''', (movie_id,))
        result = c.fetchone()
        return result["total_views"] if result else 0

    def top_views(self, limit=5):
        """
        Returns the top `limit` movies based on the total view count.
        """
        c = self.conn.cursor()
        c.execute('''
            SELECT movie_id, COUNT(*) AS view_count
            FROM views
            GROUP BY movie_id
            ORDER BY view_count DESC
            LIMIT ?
        ''', (limit,))
        results = c.fetchall()
        return [{"movie_id": row["movie_id"], "avg_rating": row["view_count"]} for row in results]

    def top_rated(self, limit=5):
        """
        Returns the top `limit` movies based on average ratings.
        """
        c = self.conn.cursor()
        c.execute('''
            SELECT movie_id, AVG(rating) AS avg_rating
            FROM ratings
            GROUP BY movie_id
            ORDER BY avg_rating DESC
            LIMIT ?
        ''', (limit,))
        results = c.fetchall()
        return [{"movie_id": row["movie_id"], "avg_rating": row["avg_rating"]} for row in results]

    def toggle_favourite(self, movie_id, user_id):
        """
        Toggles the user's favourite status for a movie.
        """
        c = self.conn.cursor()
        c.execute('''
            SELECT * FROM favourite_movies
            WHERE user_id = ? AND movie_id = ?
        ''', (user_id, movie_id))
        existing_fav = c.fetchone()
        if existing_fav:
            c.execute('''
                DELETE FROM favourite_movies
                WHERE user_id = ? AND movie_id = ?
            ''', (user_id, movie_id))
        else:
            c.execute('''
                INSERT INTO favourite_movies (user_id, movie_id)
                VALUES (?, ?)
            ''', (user_id, movie_id))
        self.conn.commit()
    

    def add_to_watchlist(self, movie_id, user_id):
        """
        Toggles the watchlist status for a movie for a user.
        If the movie is already in the watchlist, it will be removed.
        """
        c = self.conn.cursor()
        c.execute('''
            SELECT * FROM watchlist
            WHERE user_id = ? AND movie_id = ?
        ''', (user_id, movie_id))
        existing = c.fetchone()
        if existing:
            c.execute('''
                DELETE FROM watchlist
                WHERE user_id = ? AND movie_id = ?
            ''', (user_id, movie_id))
        else:
            c.execute('''
                INSERT INTO watchlist (user_id, movie_id)
                VALUES (?, ?)
            ''', (user_id, movie_id))
        self.conn.commit()

    def paginate_query(self, table, user_id, page, limit):
        c = self.conn.cursor()
        offset = (page - 1) * limit
        c.execute(f'SELECT COUNT(*) FROM {table} WHERE user_id = ?', (user_id,))
        total_items = c.fetchone()[0]
        total_pages = (total_items + limit - 1) // limit

        c.execute(f'SELECT movie_id FROM {table} WHERE user_id = ? LIMIT ? OFFSET ?', (user_id, limit, offset))
        movies = [row["movie_id"] for row in c.fetchall()]

        return {
            "current_page": page,
            "total_pages": total_pages,
            "next_page": page + 1 if page < total_pages else None,
            "previous_page": page - 1 if page > 1 else None,
            "movies": movies
        }

    def get_saved_movies(self, user_id, page=1, limit=10):
        return self.paginate_query("saved_movies", user_id, page, limit)

    def get_favourite_movies(self, user_id, page=1, limit=10):
        return self.paginate_query("favourite_movies", user_id, page, limit)

    def get_user_watchlist(self, user_id, page=1, limit=10):
        return self.paginate_query("watchlist", user_id, page, limit)


    def get_user_current_status(self, user_id, movie_id):
        c = self.conn.cursor()
        status = {}
        c.execute('''
            SELECT 1 FROM watchlist
            WHERE user_id = ? AND movie_id = ?
        ''', (user_id, movie_id))
        status["watchlist"] = bool(c.fetchone())
        
        c.execute('''
            SELECT 1 FROM favourite_movies
            WHERE user_id = ? AND movie_id = ?
        ''', (user_id, movie_id))
        status["favourite"] = bool(c.fetchone())
        
        c.execute('''
            SELECT 1 FROM saved_movies
            WHERE user_id = ? AND movie_id = ?
        ''', (user_id, movie_id))
        status["saved"] = bool(c.fetchone())
        
        return status
    def del_movie(self, movie_id):
        c = self.conn.cursor()

        tables = ["ratings", "views", "saved_movies", "favourite_movies", "watchlist"]

        for table in tables:
            c.execute(f"DELETE FROM {table} WHERE movie_id = ?", (movie_id,))

        self.conn.commit()
    



class Genres:
    def __init__(self, db_name="ratings.db"):
        self.conn = sqlite3.connect(db_name)
        self.conn.row_factory = sqlite3.Row
        self.create_table()

    def create_table(self):
        c = self.conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS genres (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE
            )
        ''')
        self.conn.commit()

    def add_genre(self, genre="Kriminal"):
        c = self.conn.cursor()
        try:
            c.execute('''
                INSERT INTO genres (name) VALUES (?)
            ''', (genre,))
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass

    def get_all_genres(self):
        c = self.conn.cursor()
        c.execute('''
            SELECT name FROM genres
        ''')
        return [row["name"] for row in c.fetchall()]

    def del_genre(self, genre):
        c = self.conn.cursor()
        c.execute('''
            DELETE FROM genres WHERE name = ?
        ''', (genre,))
        self.conn.commit()
