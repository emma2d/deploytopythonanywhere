from tmdbv3api import TMDb, Movie, Discover
import mysql.connector
import dbconfig as cfg
import requests
import os
import threading


# Initialize TMDb
tmdb = TMDb()
tmdb.api_key = 'c1482039e2c6db5fa4be2d0ed395195f'
tmdb.language = 'en'
tmdb.debug = True

discover = Discover()
movie = Movie()

# Event to signal timeout
timeout_event = threading.Event()

# Define the main function to be run with a timeout
def main():
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**cfg.db_config)
        cursor = conn.cursor()
        print("Connected successfully to the database.")

        # Create a database if not exists
        cursor.execute("CREATE DATABASE IF NOT EXISTS movies")
        cursor.execute("USE movies")

        # Create tables if not exists
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS movie_details (
            id INT PRIMARY KEY,
            title TEXT, 
            release_date DATE, 
            poster_path TEXT,
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

        # Fetch English action movies released in 2023
        while total_pages is None or page <= total_pages:
            if timeout_event.is_set():
                print("Timeout event set. Exiting...")
                break

            movie_results = discover.discover_movies({
                'primary_release_date.gte': '2023-06-01',
                'primary_release_date.lte': '2023-08-31',
                'original_language': 'en',
                'page': page
            })
            if movie_results:
                total_pages = movie_results.total_pages  # Update total_pages from API response

                for movie_data in movie_results:
                    if timeout_event.is_set():
                        print("Timeout event set. Exiting...")
                        break

                    m = movie.details(movie_data.id)
                    if m and (m.revenue != 0):  # Check if budget or revenue is not 0
                        image_name = f"{m.id}.jpg"  # Use movie id as the image name
                        cursor.execute('''
                        INSERT IGNORE INTO movie_details (id, title, release_date, poster_path, rating, vote_count, budget, revenue, runtime)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ''', (m.id, m.title, m.release_date, image_name, m.vote_average, m.vote_count, m.budget, m.revenue, m.runtime))
                        
                        # Download and save poster image
                        if m.poster_path:
                            image_url = f"https://image.tmdb.org/t/p/original{m.poster_path}"
                            image_data = requests.get(image_url).content
                            image_path = os.path.join("static", image_name)
                            with open(image_path, "wb") as image_file:
                                image_file.write(image_data)

                        cast = movie.credits(m.id)['cast']
                        num_lead_actors = 1
                        lead_cast = sorted(cast, key=lambda actor: actor['order'])[:num_lead_actors]
                        for actor in lead_cast:
                            cursor.execute('''
                            INSERT INTO actors (movie_id, title, lead_name)
                            VALUES (%s, %s, %s)
                            ''', (m.id, m.title, actor['name']))

                    conn.commit()
            page += 1  # Increment to fetch next page

    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL Database: {e}")
    finally:
        # Ensure that the connection and cursor are closed properly
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
            print("MySQL connection is closed")

# Define a wrapper function to enforce timeout
def run_with_timeout(timeout, func, *args, **kwargs):
    def wrapper():
        try:
            func(*args, **kwargs)
        except Exception as e:
            print(f"Exception in thread: {e}")

    thread = threading.Thread(target=wrapper)
    thread.start()
    thread.join(timeout)
    if thread.is_alive():
        timeout_event.set()  # Signal the timeout event
        print("Terminating script due to timeout")
        raise TimeoutError("Script runtime exceeded the maximum limit of 3 minutes")

try:
    run_with_timeout(180, main)  # 180 seconds = 3 minutes
except TimeoutError as e:
    print(e)
finally:
    timeout_event.set()  # Ensure the event is set in case of any error
