import requests
from bs4 import BeautifulSoup
import urllib
import app


def scrape_data(addr_imdb, addr_meta, addr_fone):
    req = urllib.request.Request(addr_imdb)
    req.add_header('User-Agent', 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) '
                                 'AppleWebKit/605.1.15 ( KHTML, like Gecko) Mobile/15E148')
    req.add_header('Accept-Language', 'en-US,en;q=0.8')
    page = urllib.request.urlopen(req).read().decode('utf-8')
    soup = BeautifulSoup(page, 'html.parser')

    description = soup.select('p > span')[1].text.strip()

    imdb_rating = soup.find(id="iconContext-star").parent.next_sibling.text.strip()
    imdb_rating = imdb_rating[:3]

    if soup.find(class_="score-meta") is None:
        meta_rating = ''
    else:
        meta_rating = soup.find(class_="score-meta").text.strip()

    req2 = urllib.request.Request(addr_meta)
    req2.add_header('User-Agent', 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) '
                                  'AppleWebKit/605.1.15 ( KHTML, like Gecko) Mobile/15E148')
    req2.add_header('Accept-Language', 'en-US,en;q=0.8')
    page2 = urllib.request.urlopen(req2).read().decode('utf-8')
    soup2 = BeautifulSoup(page2, 'html.parser')

    rt_audience = soup2.select('score-board')[0]['audiencescore']

    rt_critic = soup2.select('score-board')[0]['tomatometerscore']

    imdb_rating = imdb_rating[0] + imdb_rating[2]

    req3 = urllib.request.Request(addr_fone)
    req3.add_header('User-Agent', 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) '
                                  'AppleWebKit/605.1.15 ( KHTML, like Gecko) Mobile/15E148')
    req3.add_header('Accept-Language', 'en-US,en;q=0.8')

    try:
        page3 = urllib.request.urlopen(req3).read().decode('utf-8')
        soup3 = BeautifulSoup(page3, 'html.parser')

        title = soup3.find(class_="module-title").text.strip()[:-7]

        results = {'title': title, 'description': description, 'imdb_rating': imdb_rating, 'meta_rating': meta_rating,
                   'rt_audience': rt_audience, 'rt_critic': rt_critic}
        print('\nData found for:', title)
        return results

    except urllib.error.HTTPError:
        print('\nThere was an HTTP Error!')
        return None


def scrape_list():
    req = urllib.request.Request('https://www.moviefone.com/new-movie-releases/')
    req.add_header('User-Agent', 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) '
                                 'AppleWebKit/605.1.15 ( KHTML, like Gecko) Mobile/15E148')
    req.add_header('Accept-Language', 'en-US,en;q=0.8')
    page = urllib.request.urlopen(req).read().decode('utf-8')
    soup = BeautifulSoup(page, 'html.parser')

    movie_list = soup.find_all(class_='hub-movie-info')
    title_url_list = []
    for movie in movie_list:
        title = movie.text.strip()[19:]
        url = movie.contents[1]['href']
        title_url_list.append((title, url))
    print('\nNew Movie List Gathered Successfully!')
    return title_url_list


def filter_list():
    db = app.get_db()
    new_list = scrape_list()
    existing_list = db.execute('SELECT title FROM movies')
    existing_list = existing_list.fetchall()

    ex_list = []
    for title in existing_list:
        ex_list.append(title[0])

    duplicates = []
    for (title, url) in new_list:
        for t in ex_list:
            if title == t:
                duplicates.append((title, url))

    for dup in duplicates:
        new_list.remove(dup)

    print('\nNew Movie List Has Been Filtered!')
    return new_list


def find_addr():
    movie_list = filter_list()
    url_list = []
    if movie_list is None:
        return None

    for (movie, fone_url) in movie_list:
        if len(movie) > 90:
            params = {'q': movie[:89]}
        else:
            params = {'q': movie}
        headers = {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 '
                                 '( KHTML, like Gecko) Mobile/15E148', 'Accept-Language': 'en-US,en;q=0.8'}
        response = requests.get('https://www.imdb.com/find', params=params, headers=headers)
        response = response.content.decode()

        soup = BeautifulSoup(response, 'html.parser')
        url = soup.find(class_="ipc-metadata-list-summary-item__t")
        imdb_url = "https://www.imdb.com" + url['href']

        params2 = {'search': movie}
        response2 = requests.get('https://www.rottentomatoes.com/search', params=params2, headers=headers)
        response2 = response2.content.decode()

        soup2 = BeautifulSoup(response2, 'html.parser')
        url2 = soup2.select('search-page-media-row > a')
        meta_url = url2[0]['href']

        url_list.append((imdb_url, meta_url, fone_url))
        print('\nURLs found for:', movie)

    print('\nMovie Addresses Have Been Found Successfully!')
    return url_list
