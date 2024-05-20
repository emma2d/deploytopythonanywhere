# Movies Summer 2023 Application

Author: Emma Dunleavy

Student Number: g00425660

Module: Web Services & Applications

Lecturer: Andrew Beatty
***


This is the final project for the Web Services & Applications module of the Higher Diploma in Data Analytics 2023/24 at ATU. The application fetches details of English action movies released during the summer of 2023 from the TMDb API and stores them in a MySQL database. The application is designed to be deployed on PythonAnywhere. 

## Features

- Fetches movie details such as title, release date, poster, rating, vote count, budget, revenue, and runtime.
- Stores movie details in a MySQL database.
- Downloads and saves movie poster images.
- Fetches and stores lead actor details for each movie.

## Prerequisites

- Python 3.10
- Virtual environment setup
- PythonAnywhere account
- MySQL database on PythonAnywhere
- TMDb API key (provided)

## Usage

- **Fetch and store movies**:
    The script `movie_db.py` fetches movie data from TMDb and stores it in the database. Due to the extensive time required to run the script a max run time of 180 mins was coded in.  It can be run with:
    ```bash
    python movie_db.py
    ```

- **Access the web interface**:
    Navigate to [http://emma2d.pythonanywhere.com/ ](http://emma2d.pythonanywhere.com/) web app URL to access the web interface.

## Project Structure

- `movie_db.py`: Script to fetch and store movie data.
- `dbconfig.py`: Database configuration file.
- `movie_dao.py`: Data Access Object handles communication between program and database.
- `server.py`: Main application file.
- `templates/`: Directory containing HTML templates.
- `static/`: Directory containing static files (e.g., images, CSS).

  ## Requirements

- `tmdbv3api`
- `mysql-connector-python`
- `requests`

## User Instructions

bash
```
$ python -m venv venv
```
```
$ source venv/bin/activate
```
```
pip install -r requirements.txt
```

*** 

End
