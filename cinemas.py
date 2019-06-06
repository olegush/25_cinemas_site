import time
import re

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from werkzeug.contrib.cache import FileSystemCache


def get_content(url, params, cache):
    c = FileSystemCache(
        'cache',
        threshold=cache['threshold'],
        default_timeout=cache['default_timeout'])
    cache_id = url + str(params)
    cache_content = c.get(cache_id)
    if cache_content is not None:
        return cache_content
    try:
        headers = {'user-agent': UserAgent().chrome}
        resp = requests.get(url, params=params, headers=headers)
        resp.raise_for_status()
        content = resp.text
        c.set(cache_id, content)
        return content
    except requests.exceptions.Timeout as err:
        print('TimeoutError:', err)
    except requests.exceptions.HTTPError as err:
        print('HTTPError', err)
    except requests.exceptions.ConnectionError as err:
        print('ConnectionError', err)
    except requests.exceptions.RequestException as err:
        print ('Another Request Error', err)


def parse_afisha_page(content):
    soup = BeautifulSoup(content, 'html.parser')
    movies = []
    for movie in soup.find_all('div', class_='new-list__item movie-item'):
        title = movie.find('a', class_='new-list__item-link').string
        year = int(movie.find('div', class_='new-list__item-status').string[:4])
        href = movie.find('a', class_='new-list__item-link')['href']
        id_afisha = re.search('\d+', href).group(0)
        descr = ''
        descr_tag = movie.find('div', class_='new-list__item-verdict')
        if descr_tag:
            descr = descr_tag.string
        movies.append({
            'title': title,
            'year': year,
            'id_afisha': id_afisha,
            'descr': descr})
    return movies


def parse_kinopoisk_page(content, year_afisha):
    soup = BeautifulSoup(content, 'html.parser')
    try:
        for movie in soup.find_all('div', class_='element'):
            year_tag = movie.find('span', class_='year')
            year = int(year_tag.string[:4])
            #print(year)
            rating_tag = year_tag.parent.parent.parent.find('div', class_='rating')
            rating = float(rating_tag.string) if rating_tag else None
            if year == year_afisha:
                id_kinopoisk = year_tag.parent.parent.find('a')['data-id']
                return {'rating': rating, 'id_kinopoisk': id_kinopoisk}
    except (TypeError, AttributeError):
        pass
    return {'rating': None, 'id_kinopoisk': '0'}
