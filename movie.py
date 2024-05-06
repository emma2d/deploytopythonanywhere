from tmdbv3api import TMDb, Movie, Discover
import pandas as pd
import sqlite3

# Example DataFrame (assuming you have something similar)
data = {'tmdbId': [9010]}  # Replace with your actual TMDB ID list
movies = pd.DataFrame(data)

# Initialize TMDb
tmdb = TMDb()
tmdb.api_key = 'c1482039e2c6db5fa4be2d0ed395195f'
tmdb.language = 'en'
tmdb.debug = True

movie = Movie()

# Iterate through movie IDs in the dataframe
for tmdb_id in movies['tmdbId']:
    m = movie.details(tmdb_id)
    if m:  # Check if the movie details were successfully retrieved
        print(f"ID: {m.id}")
        print(f"Title: {m.title}")
        print(f"Tagline: {m.tagline}")
        print(f"Release Date: {m.release_date}")
        print(f"Original Language: {m.original_language}")
        print(f"Poster Path: {m.poster_path}")
        print(f"Backdrop Path: {m.backdrop_path}")
        print(f"Rating Count: {m.vote_count}")
        print(f"Genres: {m.genres}")
        print(f"Budget: {m.budget}")
        print(f"Revenue: {m.revenue}")
        print(f"Runtime: {m.runtime} minutes")
        print(f"Spoken Languages: {m.spoken_languages}")
        print(f"Status: {m.status}")
        print(f"Adult: {m.adult}\n")

        # Fetch cast members
        cast = movie.credits(tmdb_id)["cast"]
        lead_actors = [actor["name"] for actor in cast if actor["known_for_department"] == "Acting"]
        print(f"Lead Actors: {', '.join(lead_actors)}")
