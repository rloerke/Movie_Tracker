# Stuff

import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, render_template, flash
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


def connect_db():
    # Connects to the database.
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    # Initializes the database.
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    # Creates the database tables.
    init_db()
    print('Initialized the database.')


def get_db():
    # Opens a new database connection if there is none yet for the current application context.
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    # Closes the database again at the end of the request.
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/', methods=['GET'])
def start():
    return redirect(url_for('show_movies'))


@app.route('/movies', methods=['GET', 'POST'])
# Display notes in the database
def show_movies():
    db = get_db()
    cur = db.execute('SELECT * FROM movies ')
    movies = cur.fetchall()
    av_scores = avg_scores()

    return render_template('show_movies.html', movies=movies, av_scores=av_scores)


@app.route('/add')
# Redirects to a form for writing notes
def add_movie():
    return render_template('add_movie.html')


@app.route('/add-db', methods=['POST'])
# Adds a new note to the database
def add_db():
    db = get_db()

    # Add the post into the database
    db.execute('INSERT INTO movies (title, description, imdbRating, metaRating, rtAudienceRating, rtCriticRating) '
               'VALUES (?, ?, ?, ?, ?, ?)',
               [request.form['title'], request.form['description'], request.form['imdb'],
                request.form['meta'], request.form['rt_audience'], request.form['rt_critic']])
    db.commit()

    # Notify the user their post was made successfully
    flash('Your Movie has been added successfully!')
    return redirect(url_for('start'))


@app.route('/scrape', methods=['POST'])
def scrape_movies():
    db = get_db()
    url_list = scrape.find_addr()

    for (imdb_url, meta_url, fone_url) in url_list:
        data = scrape.scrape_data(imdb_url, meta_url, fone_url)

        if data is not None:
            db.execute('INSERT INTO movies '
                       '(title, description, imdbRating, metaRating, rtAudienceRating, rtCriticRating) '
                       'VALUES (?, ?, ?, ?, ?, ?)', [data['title'], data['description'], data['imdb_rating'],
                                                     data['meta_rating'], data['rt_audience'], data['rt_critic']])
            db.commit()

    # Notify the user their post was made successfully
    flash('Your Movie List has been Updated Successfully!')
    return redirect(url_for('start'))


def avg_scores():
    db = get_db()
    av_scores = {}
    titles = db.execute('SELECT title FROM movies')

    for movie in titles:
        av_scores[movie[0]] = db.execute('SELECT ((Coalesce(imdbRating,0) + Coalesce(metaRating,0) + '
                                         'Coalesce(rtAudienceRating,0) + Coalesce(rtCriticRating,0)) '
                                         '/(Coalesce(imdbRating/imdbRating, 0) + Coalesce(metaRating/metaRating, 0) + '
                                         'Coalesce(rtAudienceRating/rtAudienceRating, 0) + '
                                         'Coalesce(rtCriticRating/rtCriticRating, 0))) FROM movies WHERE title = ?',
                                         [movie[0]]).fetchall()[0][0]

    return av_scores
