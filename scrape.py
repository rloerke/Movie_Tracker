import requests
from bs4 import BeautifulSoup
import urllib
import app


def scrape_data(addr_imdb, addr_meta):
    req = urllib.request.Request(addr_imdb)
    req.add_header('User-Agent', 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) '
                                 'AppleWebKit/605.1.15 ( KHTML, like Gecko) Mobile/15E148')
    req.add_header('Accept-Language', 'en-US,en;q=0.8')
    page = urllib.request.urlopen(req).read().decode('utf-8')
    soup = BeautifulSoup(page, 'html.parser')

    title = soup.select('title')[0].text.strip()
    title = title[:(len(title) - 14)]
    # print('\n\n', title)

    description = soup.select('p')[0].text.strip()
    # print('\n', description)

    # imdb_rating = soup.select('a')[49].text.strip()
    imdb_rating = soup.find(id="iconContext-star").parent.next_sibling.text.strip()
    imdb_rating = imdb_rating[:3]
    # print('\n\n', imdb_rating)

    meta_rating = soup.find(class_="score-meta").text.strip()
    # print('\n\n', meta_rating)

    req2 = urllib.request.Request(addr_meta)
    req2.add_header('User-Agent', 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) '
                                  'AppleWebKit/605.1.15 ( KHTML, like Gecko) Mobile/15E148')
    req2.add_header('Accept-Language', 'en-US,en;q=0.8')
    page2 = urllib.request.urlopen(req2).read().decode('utf-8')
    soup2 = BeautifulSoup(page2, 'html.parser')

    rt_audience = soup2.select('score-board')[0]['audiencescore']
    # print('\n\n', rt_audience)

    rt_critic = soup2.select('score-board')[0]['tomatometerscore']
    # print('\n\n', rt_critic)

    imdb_rating = imdb_rating[0] + imdb_rating[2]

    results = {'title': title, 'description': description, 'imdb_rating': imdb_rating, 'meta_rating': meta_rating,
               'rt_audience': rt_audience, 'rt_critic': rt_critic}
    print('\n\n', results)
    return results


def scrape_list():
    req = urllib.request.Request('https://www.moviefone.com/new-movie-releases/')
    req.add_header('User-Agent', 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) '
                                 'AppleWebKit/605.1.15 ( KHTML, like Gecko) Mobile/15E148')
    req.add_header('Accept-Language', 'en-US,en;q=0.8')
    page = urllib.request.urlopen(req).read().decode('utf-8')
    soup = BeautifulSoup(page, 'html.parser')

    movie_list = soup.find_all(class_='hub-movie-info')
    list_clean = []
    for movie in movie_list:
        list_clean.append(movie.text.strip()[19:])
    print('\n\n', list_clean)
    return list_clean


def filter_list():
    db = app.get_db()
    init_list = scrape_list()
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
    # return init_list
    return init_list[:5]


def find_addr():
    movie_list = filter_list()
    url_list = []

    for movie in movie_list:
        params = {'q': movie}
        headers = {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 '
                                 '( KHTML, like Gecko) Mobile/15E148', 'Accept-Language': 'en-US,en;q=0.8'}
        response = requests.get('https://www.imdb.com/find', params=params, headers=headers)
        response = response.content.decode()
        # print('\n\n', response)

        soup = BeautifulSoup(response, 'html.parser')
        url = soup.find(class_="ipc-metadata-list-summary-item__t")
        imdb_url = "https://www.imdb.com/" + url['href']
        print('\n\n', imdb_url)

        params2 = {'search': movie}
        response2 = requests.get('https://www.rottentomatoes.com/search', params=params2, headers=headers)
        response2 = response2.content.decode()
        # print('\n\n', response2)

        soup2 = BeautifulSoup(response2, 'html.parser')
        url2 = soup2.select('search-page-media-row > a')
        meta_url = url2[0]['href']
        print('\n\n', meta_url)

        url_list.append((imdb_url, meta_url))

    print('\n\n', url_list)
    return url_list


# scrape_data('https://www.imdb.com/title/tt1397514/',
#            'https://www.rottentomatoes.com/m/journey_to_the_center_of_the_earth_2_3d')
