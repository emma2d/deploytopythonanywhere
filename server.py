
from flask import Flask, request, jsonify
import mysql.connector
import dbconfig as cfg

app = Flask(__name__)

# Setup MySQL database connection
def get_db_connection():
    try:
        conn = mysql.connector.connect(cfg.mysql)
    except Exception as e:
        print(f"Error: {e}")
    return conn

@app.route('/')
def index():
    return "Welcome to the Movie API!"

# Create a new movie
@app.route('/movies', methods=['POST'])
def add_movie():
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO movie_details (id, title, release_date, poster_path, rating, vote_count, budget, revenue, runtime)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (data['id'], data['title'], data['release_date'], data['poster_path'], data['rating'], data['vote_count'], data['budget'], data['revenue'], data['runtime']))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'}), 201

# Get all movies
@app.route('/movies', methods=['GET'])
def get_movies():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM movie_details')
    movies = cursor.fetchall()
    conn.close()
    return jsonify(movies)

# Update a movie
@app.route('/movies/<int:movie_id>', methods=['PUT'])
def update_movie(movie_id):
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE movie_details
        SET title=%s, release_date=%s, poster_path=%s, rating=%s, vote_count=%s, budget=%s, revenue=%s, runtime=%s
        WHERE id=%s
    ''', (data['title'], data['release_date'], data['poster_path'], data['rating'], data['vote_count'], data['budget'], data['revenue'], data['runtime'], movie_id))
    conn.commit()
    conn.close()
    return jsonify({'status': 'updated'}), 200

# Delete a movie
@app.route('/movies/<int:movie_id>', methods=['DELETE'])
def delete_movie(movie_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM movie_details WHERE id=%s', (movie_id,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'deleted'}), 204

if __name__ == '__main__':
    app.run(debug=True)
