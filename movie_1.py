from tmdbv3api import TMDb, Movie, Discover
import pandas as pd
import sqlite3

# Initialize TMDb
tmdb = TMDb()
tmdb.api_key = 'c1482039e2c6db5fa4be2d0ed395195f'
tmdb.language = 'en'
tmdb.debug = True

discover = Discover()
movie = Movie()

# Fetch movies released in 2023
movies_2023 = discover.discover_movies({
    'primary_release_year': 2023
})

# Fetch movies released in 2023
movie_results = discover.discover_movies({
    'primary_release_year': 2023 })

# Example: Fetch only a subset for demo purposes
movies_2023 = list(movie_results)[:5]  # Reduce the number for demonstration

# Connect to SQLite database
conn = sqlite3.connect('movies.db')
c = conn.cursor()

# Create tables
c.execute('''
CREATE TABLE IF NOT EXISTS movie_details (
    id INTEGER PRIMARY KEY,
    title TEXT,
    tagline TEXT,
    release_date TEXT,
    original_language TEXT,
    poster_path TEXT,
    backdrop_path TEXT,
    vote_count INTEGER,
    budget INTEGER,
    revenue INTEGER,
    runtime INTEGER,
    spoken_languages TEXT,
    status TEXT,
    adult INTEGER
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS actors (
    actor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    movie_id INTEGER,
    name TEXT,
    FOREIGN KEY (movie_id) REFERENCES movie_details (id)
)
''')

# Iterate through each movie
for movie_data in movies_2023:
    m = movie.details(movie_data.id)
    if m:
        # Insert movie details into movie_details table
        c.execute('''
        INSERT INTO movie_details (id, title, tagline, release_date, original_language, poster_path, backdrop_path, vote_count, budget, revenue, runtime, spoken_languages, status, adult)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (m.id, m.title, m.tagline, m.release_date, m.original_language, m.poster_path, m.backdrop_path, m.vote_count, m.budget, m.revenue, m.runtime, str(m.spoken_languages), m.status, m.adult))

        # Fetch and insert actors
        cast = movie.credits(m.id)['cast']
        for actor in cast:
            if actor['known_for_department'] == 'Acting':
                c.execute('''
                INSERT INTO actors (movie_id, name)
                VALUES (?, ?)
                ''', (m.id, actor['name']))

# Commit changes and close connection
conn.commit()
conn.close()
