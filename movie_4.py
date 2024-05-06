from tmdbv3api import TMDb, Movie, Discover
import mysql.connector

# Initialize TMDb
tmdb = TMDb()
tmdb.api_key = 'c1482039e2c6db5fa4be2d0ed395195f'
tmdb.language = 'en'
tmdb.debug = True

discover = Discover()
movie = Movie()

# Setup MySQL database connection
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
    runtime INT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS actors (
    actor_id INT AUTO_INCREMENT PRIMARY KEY,
    movie_id INT,
    title TEXT,
    lead_name TEXT,
    FOREIGN KEY (movie_id) REFERENCES movie_details (id)
)
''')

# Pagination setup
page = 1
total_pages = None

# Fetch movies released between 2020 and 2024
while total_pages is None or page <= total_pages:
    movie_results = discover.discover_movies({
        'primary_release_date.gte': '2023-01-01',
        'primary_release_date.lte': '2023-12-31',
        'page': page
    })
    total_pages = movie_results.total_pages  # Update total_pages from API response

    for movie_data in movie_results:
        m = movie.details(movie_data.id)
        if m:
            cursor.execute('''
            INSERT INTO movie_details (id, title, release_date, poster_path, backdrop_path, rating, vote_count, budget, revenue, runtime)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (m.id, m.title, m.release_date, m.poster_path, m.backdrop_path, m.vote_average, m.vote_count, m.budget, m.revenue, m.runtime))
            
            cast = movie.credits(m.id)['cast']
            num_lead_actors = 1
            lead_cast = sorted(cast, key=lambda actor: actor['order'])[:num_lead_actors]
            for actor in lead_cast:
                cursor.execute('''
                INSERT INTO actors (movie_id, title, lead_name)
                VALUES (%s, (%s, %s)
                ''', (m.id, m.title, actor['name']))

    conn.commit()
    page += 1  # Increment to fetch next page

# Close connection
conn.close()
