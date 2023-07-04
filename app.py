# Stuff

import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, render_template, flash
import scrape
import requests
from bs4 import BeautifulSoup

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
    find_addr()
    return redirect(url_for('show_movies'))


@app.route('/movies', methods=['GET', 'POST'])
# Display notes in the database
def show_movies():
    db = get_db()
    cur = db.execute('SELECT * FROM movies ')
    movies = cur.fetchall()

    return render_template('show_movies.html', movies=movies)


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


@app.route('/insert', methods=['POST'])
def insert_movie():
    db = get_db()
    data = scrape.scrape_data('https://www.imdb.com/title/tt1397514/',
                              'https://www.rottentomatoes.com/m/journey_to_the_center_of_the_earth_2_3d')
    db.execute('INSERT INTO movies (title, description, imdbRating, metaRating, rtAudienceRating, rtCriticRating) '
               'VALUES (?, ?, ?, ?, ?, ?)', [data['title'], data['description'], data['imdb_rating'],
                                             data['meta_rating'], data['rt_audience'], data['rt_critic']])
    db.commit()

    # Notify the user their post was made successfully
    flash('Your Movie has been inserted successfully!')
    return redirect(url_for('start'))


def filter_list():
    db = get_db()
    init_list = scrape.scrape_list()
    existing_list = db.execute('SELECT title FROM movies')
    existing_list = existing_list.fetchall()

    ex_list = []
    for title in existing_list:
        ex_list.append(title[0])
    # print(ex_list, '\n\n', init_list)

    for title in init_list:
        for t in ex_list:
            if title == t:
                init_list.remove(title)

    print('\n\n', init_list)
    return init_list


def find_addr():
    movie_list = filter_list()

    params = {'q': movie_list[0]}
    headers = {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 '
                             '( KHTML, like Gecko) Mobile/15E148', 'Accept-Language': 'en-US,en;q=0.8'}
    response = requests.get('https://www.imdb.com/find', params=params, headers=headers)
    response = response.content.decode()
    # print('\n\n', response)

    soup = BeautifulSoup(response, 'html.parser')
    url = soup.find(class_="ipc-metadata-list-summary-item__t")
    imdb_url = "https://www.imdb.com/" + url['href']
    print('\n\n', imdb_url)

    params2 = {'search': movie_list[0]}
    response2 = requests.get('https://www.rottentomatoes.com/search', params=params2, headers=headers)
    response2 = response2.content.decode()
    # print('\n\n', response2)

    soup2 = BeautifulSoup(response2, 'html.parser')
    url2 = soup2.select('search-page-media-row > a')
    meta_url = url2[0]['href']
    print('\n\n', meta_url)
