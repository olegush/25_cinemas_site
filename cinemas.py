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
    headers = {'user-agent': UserAgent().chrome}
    resp = requests.get(url, params=params, headers=headers)
    resp.raise_for_status()
    content = resp.text
    c.set(cache_id, content)
    return content


def parse_afisha_page(content):
    soup = BeautifulSoup(content, 'html.parser')
    movies = []
    for movie in soup.find_all('div', class_='new-list__item movie-item'):
        title = movie.find('a', class_='new-list__item-link').text
        year = int(movie.find('div', class_='new-list__item-status').text[:4])
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


def parse_kinopoisk_page(content, year):
    soup = BeautifulSoup(content, 'html.parser')
    try:
        for movie in soup.find_all('div', class_='element'):
            year_kp_tag = movie.find('span', class_='year')
            year_kp = int(year_kp_tag.string[:4])
            rating_tag = year_kp_tag.parent.parent.parent.find('div', class_='rating')
            rating_kp = float(rating_tag.string) if rating_tag else None
            if year_kp == year:
                title_eng_tag = movie.find('span', class_='gray').text.rpartition(',')
                title_eng = title_eng_tag[0]
                runtime = title_eng_tag[2].strip()
                id_kinopoisk = year_kp_tag.parent.parent.find('a')['data-id']
                return {'rating_kp': rating_kp, 'id_kinopoisk': id_kinopoisk, 'title_eng': title_eng, 'runtime':  runtime}
    except (TypeError, AttributeError):
        pass
    return {'rating_kp': None, 'id_kinopoisk': '0', 'title_eng': '', 'runtime': ''}


def parse_imdb_page(content, year):
    soup = BeautifulSoup(content, 'html.parser')
    try:
        for movie in soup.find_all('div', class_='rating rating-list'):
            imdb = movie['id'].split('|')
            id_imdb = imdb[0]
            rating_imdb = imdb[2]
            return {'id_imdb': id_imdb, 'rating_imdb': rating_imdb}
    except (TypeError, AttributeError):
        return {'id_imdb': '', 'rating_imdb': ''}
