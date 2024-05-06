from tmdbv3api import TMDb, Movie, Discover
import pandas as pd
import mysql.connector

# Initialize TMDb
tmdb = TMDb()
tmdb.api_key = 'c1482039e2c6db5fa4be2d0ed395195f'
tmdb.language = 'en'
tmdb.debug = True

discover = Discover()
movie = Movie()

# Fetch movies released between 2020 and 2024
movie_results = discover.discover_movies({
    'primary_release_date.gte': '2020-01-01',  # Release date greater than or equal to January 1, 2000
    'primary_release_date.lte': '2024-04-30'  # Release date less than or equal to December 31, 2024
})

# Example: Fetch only a subset for demo purposes
movies_2023 = list(movie_results) 

# Connect to MySQL database
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Infinity1!",
    database="movies"
)
cursor = conn.cursor()

# Create tables if not exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS movie_details (
    id INT PRIMARY KEY,
    title TEXT, 
    release_date DATE, 
    poster_path TEXT,
    backdrop_path TEXT,
    rating FLOAT,
    vote_count INT,
    budget INT,
    revenue INT,
    runtime INT,
    status TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS actors (
    actor_id INT AUTO_INCREMENT PRIMARY KEY,
    movie_id INT,
    name TEXT,
    FOREIGN KEY (movie_id) REFERENCES movie_details (id)
)
''')

# Iterate through each movie
for movie_data in movies_2023:
    m = movie.details(movie_data.id)
    if m:
        # Insert movie details into movie_details table
        cursor.execute('''
        INSERT INTO movie_details (id, title, release_date, poster_path, backdrop_path, rating, vote_count, budget, revenue, runtime, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (m.id, m.title, m.release_date, m.poster_path, m.backdrop_path, m.vote_average, m.vote_count, m.budget, m.revenue, m.runtime, m.status))

        # Fetch and insert actors
        cast = movie.credits(m.id)['cast']
        num_lead_actors = 3
        lead_cast = sorted(cast, key=lambda actor: actor['order'])[:num_lead_actors]
        for actor in lead_cast:
            cursor.execute('''
            INSERT INTO actors (movie_id, name)
            VALUES (%s, %s)
            ''', (m.id, actor['name']))

# Commit changes and close connection
conn.commit()
conn.close()
