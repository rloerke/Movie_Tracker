import requests
from bs4 import BeautifulSoup
import urllib

req = urllib.request.Request('https://www.imdb.com/title/tt1397514/')
req.add_header('User-Agent',
               'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 ( KHTML, like Gecko) Mobile/15E148')
page = urllib.request.urlopen(req).read().decode('utf-8')
soup = BeautifulSoup(page, 'html.parser')

title = soup.select('title')[0].text.strip()
title = title[:(len(title) - 7)]
print('\n\n', title)

description = soup.select('p')[0].text.strip()
print('\n', description)

#imdbRating = soup.select('a')[49].text.strip()
imdbRating = soup.find(id="iconContext-star").parent.next_sibling.text.strip()
imdbRating = imdbRating[:3]
print('\n\n', imdbRating)

metaRating = soup.find(class_="score-meta").text.strip()
print('\n\n', metaRating)

req2 = urllib.request.Request('https://www.rottentomatoes.com/m/journey_to_the_center_of_the_earth_2_3d')
req2.add_header('User-Agent',
                'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 ( KHTML, like Gecko) Mobile/15E148')
page2 = urllib.request.urlopen(req2).read().decode('utf-8')
soup2 = BeautifulSoup(page2, 'html.parser')

rt_audience = soup2.select('score-board')[0]['audiencescore']
print('\n\n', rt_audience)

rt_critic = soup2.select('score-board')[0]['tomatometerscore']
print('\n\n', rt_critic)

imdbRating = imdbRating[0] + imdbRating[2]

results = {'title': title, 'description': description, 'imdbRating': imdbRating, 'metaRating': metaRating,
           'rt_audience': rt_audience, 'rt_critic': rt_critic}
print('\n\n', results)
