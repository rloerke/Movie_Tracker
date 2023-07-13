# Movie Tracker is a program that scrapes data about new movies and compiles that data into an easy-to-use database
# This is the main file that creates the database and webpage where its table can be viewed
# Written by Ray Loerke

import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, g, redirect, url_for, render_template, flash
import scrape

# Create the application
app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'movie_tracker.db'),
    DEBUG=True,
    SECRET_KEY='development key',
))
app.config.from_envvar('Movie_Tracker_SETTINGS', silent=True)


# Connects to the database.
def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


# Initializes the database.
def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
# Creates the database tables.
def initdb_command():
    init_db()
    print('Initialized the database.')


# Opens a new database connection if there is none yet for the current application context.
def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
# Closes the database again at the end of the request and print any errors.
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()
    if error is not None:
        print("Error:", error)


@app.route('/', methods=['GET', 'POST'])
# Display movies in the database
def show_movies():
    # Get the movie data from the database
    db = get_db()
    cur = db.execute('SELECT * FROM movies ')
    movies = cur.fetchall()

    # Calculate the average score for each movie
    av_scores = avg_scores()

    # Pass the necessary info to the template and render
    return render_template('show_movies.html', movies=movies, av_scores=av_scores)


@app.route('/add')
# Redirects to a form for manually entering a movie
def add_movie():
    return render_template('add_movie.html')


@app.route('/add-db', methods=['POST'])
# Adds a new movie to the database
def add_db():
    db = get_db()

    # Add the movie data into the database
    db.execute('INSERT INTO movies (title, description, imdbRating, metaRating, rtAudienceRating, rtCriticRating) '
               'VALUES (?, ?, ?, ?, ?, ?)',
               [request.form['title'], request.form['description'], request.form['imdb'],
                request.form['meta'], request.form['rt_audience'], request.form['rt_critic']])
    db.commit()

    # Notify the user their movie was added successfully
    flash('Your Movie has been added successfully!')
    return redirect(url_for('show_movies'))


@app.route('/scrape', methods=['POST'])
# Search the internet for newly released movies and add their data to the movie database
def scrape_movies():
    db = get_db()

    # Calls a function from scrape.py that finds a list of newly released movies, then finds
    # IMDB, Metacritic, and MovieFone urls that can be searched for movie data
    url_list = scrape.find_addr()

    # For each new movie we search the urls for movie data
    for (imdb_url, meta_url, f_url) in url_list:
        data = scrape.scrape_data(imdb_url, meta_url, f_url)

        # This movie data is then added to the movie database
        if data is not None:
            db.execute('INSERT INTO movies '
                       '(title, description, imdbRating, metaRating, rtAudienceRating, rtCriticRating) '
                       'VALUES (?, ?, ?, ?, ?, ?)', [data['title'], data['description'], data['imdb_rating'],
                                                     data['meta_rating'], data['rt_audience'], data['rt_critic']])
            db.commit()

    # Notify the user their movie list was updated successfully
    flash('Your Movie List has been Updated Successfully!')
    return redirect(url_for('show_movies'))


@app.route('/del', methods=['POST', 'GET'])
# Removes a movie from the database
def delete_movie():
    # Removes the movie from the database with the matching movie id
    db = get_db()
    db.execute('DELETE FROM movies WHERE movieID = ?', [request.args.get('id')])
    db.commit()

    # Notify the user the movie was removed
    flash('Movie was Removed')
    return redirect(url_for('show_movies'))


@app.route('/edit', methods=['POST', 'GET'])
# Redirects to a form for editing a movies data
def edit_movie():
    # Get the current movie data to display to the user
    db = get_db()
    cur = db.execute('SELECT * FROM movies WHERE movieID = ?', [request.args.get('id')])
    m_data = cur.fetchone()

    # Render the template with this existing movie data
    return render_template('edit_movie.html', data=m_data)


@app.route('/edit-db', methods=['POST'])
# Edits a movie already in the database
def edit_db():
    # Update the database with the new movie data
    db = get_db()
    db.execute('UPDATE movies SET title=?, description=?, imdbRating=?, metaRating=?, rtAudienceRating=?, '
               'rtCriticRating=? WHERE movieID=?', [request.form['title'], request.form['description'],
                                                    request.form['imdbRating'], request.form['metaRating'],
                                                    request.form['rtAudienceRating'], request.form['rtCriticRating'],
                                                    request.form['movieID']])
    db.commit()
    return redirect(url_for('show_movies'))


# Calculates the average rating for each movie in the database
def avg_scores():
    db = get_db()

    # Create the dictionary that will hold our average ratings and get a list of movies in the database
    av_scores = {}
    titles = db.execute('SELECT title FROM movies')

    # For each movie in the database average together its ratings and add that average to the dictionary
    for movie in titles:

        # Coalesce is used to handle cases where no rating is available for a given column
        av_scores[movie[0]] = db.execute('SELECT ((Coalesce(imdbRating,0) + Coalesce(metaRating,0) + '
                                         'Coalesce(rtAudienceRating,0) + Coalesce(rtCriticRating,0)) '
                                         '/(Coalesce(imdbRating/imdbRating, 0) + Coalesce(metaRating/metaRating, 0) + '
                                         'Coalesce(rtAudienceRating/rtAudienceRating, 0) + '
                                         'Coalesce(rtCriticRating/rtCriticRating, 0))) FROM movies WHERE title = ?',
                                         [movie[0]]).fetchall()[0][0]

    return av_scores
