import mysql.connector
from mysql.connector import Error

class MovieDAO:
    def __init__(self, db_config):
        self.db_config = db_config

    def connect(self):
        return mysql.connector.connect(**self.db_config)

    def fetch_all_movies(self):
        with self.connect() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM movie_details")
            return cursor.fetchall()
    
    def fetch_movie_by_id(self, movie_id):
        with self.connect() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM movie_details WHERE id = %s", (movie_id,))
            return cursor.fetchone()

    def insert_movie(self, movie):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO movie_details (id, title, release_date, poster_path, rating, vote_count, budget, revenue, runtime)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (movie['id'], movie['title'], movie['release_date'], movie['poster_path'], movie['rating'], movie['vote_count'], movie['budget'], movie['revenue'], movie['runtime']))
            conn.commit()
            return cursor.lastrowid

    def update_movie(self, movie_id, movie):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE movie_details
                SET title=%s, release_date=%s, poster_path=%s, rating=%s, vote_count=%s, budget=%s, revenue=%s, runtime=%s
                WHERE id=%s
            ''', (movie['title'], movie['release_date'], movie['poster_path'], movie['rating'], movie['vote_count'], movie['budget'], movie['revenue'], movie['runtime'], movie_id))
            conn.commit()
            return cursor.rowcount

    def delete_movie(self, movie_id):
        with self.connect() as conn:
            # Delete associated records from the actors table first
            self.delete_actors_for_movie(movie_id, conn)
            
            cursor = conn.cursor()
            cursor.execute('DELETE FROM movie_details WHERE id=%s', (movie_id,))
            conn.commit()
            return cursor.rowcount

    def delete_actors_for_movie(self, movie_id, conn):
        cursor = conn.cursor()
        cursor.execute('DELETE FROM actors WHERE movie_id=%s', (movie_id,))
        conn.commit()

    def fetch_actors_by_movie(self, movie_id):
        with self.connect() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT lead_name FROM actors WHERE movie_id = %s", (movie_id,))
            return cursor.fetchall()
    
    def fetch_highest_grossing_movie(self):
        with self.connect() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute('''
                SELECT m.title, a.lead_name, m.revenue
                FROM movie_details m
                JOIN actors a ON m.id = a.movie_id
                WHERE a.actor_id = (
                    SELECT MIN(actor_id)
                    FROM actors
                    WHERE movie_id = m.id
                )
                ORDER BY m.revenue DESC
                LIMIT 1
            ''')
            return cursor.fetchone()