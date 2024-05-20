from flask import Flask, request, jsonify, render_template
from movie_dao import MovieDAO 
import dbconfig as cfg

app = Flask(__name__, static_folder='static')
dao = MovieDAO(cfg.mysql)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/movies', methods=['GET'])
def get_movies():
    movies = dao.fetch_all_movies()
    return jsonify(movies)

@app.route('/movies/<int:movie_id>', methods=['GET'])
def get_movie(movie_id):
    # Fetch details of the movie with the specified ID
    movie = dao.fetch_movie_by_id(movie_id)
    if movie:
        return jsonify(movie)
    else:
        return jsonify({'error': 'Movie not found'}), 404

@app.route('/movies', methods=['POST'])
def add_movie():
    movie_data = request.get_json()
    movie_id = dao.insert_movie(movie_data)
    return jsonify({'status': 'success', 'movie_id': movie_id}), 201

@app.route('/movies/<int:movie_id>', methods=['PUT'])
def update_movie(movie_id):
    movie_data = request.get_json()
    updated_rows = dao.update_movie(movie_id, movie_data)
    return jsonify({'status': 'updated', 'updated_rows': updated_rows}), 200

@app.route('/movies/<int:movie_id>', methods=['DELETE'])
def delete_movie(movie_id):
    deleted_rows = dao.delete_movie(movie_id)
    return jsonify({'status': 'deleted', 'deleted_rows': deleted_rows}), 204

@app.route('/movies/<int:movie_id>/actors', methods=['GET'])
def get_actors_by_movie(movie_id):
    try:
        actors = dao.fetch_actors_by_movie(movie_id)
        return jsonify(actors), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/movies/highest-grossing', methods=['GET'])
def get_highest_grossing_movie():
    try:
        highest_grossing_movie = dao.fetch_highest_grossing_movie()
        if highest_grossing_movie:
            return jsonify(highest_grossing_movie), 200
        else:
            return jsonify({'message': 'No movies found.'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
