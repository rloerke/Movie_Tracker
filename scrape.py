# Movie Tracker is a program that scrapes data about new movies and compiles that data into an easy-to-use database
# This is the file that searches the internet for new movies,
# finds urls for those new movies, and scrapes those urls for movie data
# Written by Ray Loerke

import requests
from bs4 import BeautifulSoup
import urllib
import app


# Scrapes movie data from the given urls (IMDB, Metacritic, MovieFone)
def scrape_data(addr_imdb, addr_meta, addr_fone):
    # Gather the html from the IMDB url
    req = urllib.request.Request(addr_imdb)

    # Headers are added so the site can identify our request
    req.add_header('User-Agent', 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) '
                                 'AppleWebKit/605.1.15 ( KHTML, like Gecko) Mobile/15E148')
    req.add_header('Accept-Language', 'en-US,en;q=0.8')
    page = urllib.request.urlopen(req).read().decode('utf-8')

    # Beautiful Soup is used to parse the html
    soup = BeautifulSoup(page, 'html.parser')

    # The movies description is pulled out of the html and converted into a string
    description = soup.select('p > span')[1].text.strip()

    # The IMDB score is pulled out of the html
    imdb_rating = soup.find(id="iconContext-star").parent.next_sibling.text.strip()
    imdb_rating = imdb_rating[:3]

    # The IMDB rating is converted from a 1/10 format into a 1/100 format to match the other ratings
    imdb_rating = imdb_rating[0] + imdb_rating[2]

    # If the movie has a Metacritic rating, pull it out of the html
    if soup.find(class_="score-meta") is None:
        meta_rating = ''
    else:
        meta_rating = soup.find(class_="score-meta").text.strip()

    # The html is gathered from the Metacritic url
    req2 = urllib.request.Request(addr_meta)

    # Headers are added so the site can identify our request
    req2.add_header('User-Agent', 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) '
                                  'AppleWebKit/605.1.15 ( KHTML, like Gecko) Mobile/15E148')
    req2.add_header('Accept-Language', 'en-US,en;q=0.8')

    # Beautiful Soup is used to parse the html
    page2 = urllib.request.urlopen(req2).read().decode('utf-8')
    soup2 = BeautifulSoup(page2, 'html.parser')

    # The Rotten Tomatoes audience and critic scores are pulled from the html
    rt_audience = soup2.select('score-board')[0]['audiencescore']
    rt_critic = soup2.select('score-board')[0]['tomatometerscore']

    # The html is gathered from the Movie Fone url
    req3 = urllib.request.Request(addr_fone)

    # Headers are added so the site can identify our request
    req3.add_header('User-Agent', 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) '
                                  'AppleWebKit/605.1.15 ( KHTML, like Gecko) Mobile/15E148')
    req3.add_header('Accept-Language', 'en-US,en;q=0.8')

    # This try block will catch errors if the Movie Fone page for the current movie can't be found
    try:
        # Beautiful Soup is used to parse the html
        page3 = urllib.request.urlopen(req3).read().decode('utf-8')
        soup3 = BeautifulSoup(page3, 'html.parser')

        # The movie's title is pulled from the html
        title = soup3.find(class_="module-title").text.strip()[:-7]

        # All the movie data is then added into a dictionary which is returned
        results = {'title': title, 'description': description, 'imdb_rating': imdb_rating, 'meta_rating': meta_rating,
                   'rt_audience': rt_audience, 'rt_critic': rt_critic}
        print('\nData found for:', title)
        return results

    except urllib.error.HTTPError:
        print('\nThere was an HTTP Error!')
        return None


# Searches the Movie Fone site for new movie releases
def scrape_list():
    # The html is gathered from the Movie Fone url
    req = urllib.request.Request('https://www.moviefone.com/new-movie-releases/')

    # Headers are added so the site can identify our request
    req.add_header('User-Agent', 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) '
                                 'AppleWebKit/605.1.15 ( KHTML, like Gecko) Mobile/15E148')
    req.add_header('Accept-Language', 'en-US,en;q=0.8')

    # Beautiful Soup is used to parse the html
    page = urllib.request.urlopen(req).read().decode('utf-8')
    soup = BeautifulSoup(page, 'html.parser')

    # The new movies are pulled from the html and put into a list
    movie_list = soup.find_all(class_='hub-movie-info')
    title_url_list = []

    # For each movie in the list the title and url are isolated
    for movie in movie_list:
        title = movie.text.strip()[19:]
        url = movie.contents[1]['href']

        # The title and url are then added to a list that gets returned
        title_url_list.append((title, url))
    print('\nNew Movie List Gathered Successfully!')
    return title_url_list


# Filters out movies that are already in the database
def filter_list():
    db = app.get_db()

    # Call a function to get a list of newly released movies
    new_list = scrape_list()

    # Create a list of movies already in the database
    existing_list = db.execute('SELECT title FROM movies')
    existing_list = existing_list.fetchall()

    # Convert this list into a new list of strings for each movie's title
    ex_list = []
    for title in existing_list:
        ex_list.append(title[0])

    # Check the items in both lists against each other and create a list of duplicate movies
    duplicates = []
    for (title, url) in new_list:
        for t in ex_list:
            if title == t:
                duplicates.append((title, url))

    # Remove the duplicate movies from the list of new movie releases
    for dup in duplicates:
        new_list.remove(dup)

    # Return the filtered list
    print('\nNew Movie List Has Been Filtered!')
    return new_list


# Finds the IMDB and Metacritic urls for a list of movies
def find_addr():

    # Calls a function to gather a list of newly released movies not already in the database
    movie_list = filter_list()
    url_list = []

    # If there are no new movies end the function
    if movie_list is None:
        return None

    # Loop through each movie in the list
    for (movie, fone_url) in movie_list:

        # Shorten movie titles if they are too long
        if len(movie) > 90:
            params = {'q': movie[:89]}
        else:
            params = {'q': movie}

        # Headers are added so the site can identify our request
        headers = {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 '
                                 '( KHTML, like Gecko) Mobile/15E148', 'Accept-Language': 'en-US,en;q=0.8'}

        # The html is gathered from the IMDB url
        response = requests.get('https://www.imdb.com/find', params=params, headers=headers)

        # Beautiful Soup is used to parse the html
        response = response.content.decode()
        soup = BeautifulSoup(response, 'html.parser')

        # The IMDB url is pulled out of the html
        url = soup.find(class_="ipc-metadata-list-summary-item__t")
        imdb_url = "https://www.imdb.com" + url['href']

        # The html is gathered from the Rotten Tomatoes url
        params2 = {'search': movie}
        response2 = requests.get('https://www.rottentomatoes.com/search', params=params2, headers=headers)

        # Beautiful Soup is used to parse the html
        response2 = response2.content.decode()

        # The Rotten Tomatoes url is pulled from the html
        soup2 = BeautifulSoup(response2, 'html.parser')
        url2 = soup2.select('search-page-media-row > a')
        rt_url = url2[0]['href']

        # The urls are added to a list which is then returned
        url_list.append((imdb_url, rt_url, fone_url))
        print('\nURLs found for:', movie)

    print('\nMovie Addresses Have Been Found Successfully!')
    return url_list
