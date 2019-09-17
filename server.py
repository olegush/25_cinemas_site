import os

import requests
from dotenv import load_dotenv
import concurrent.futures
from flask import Flask, render_template, jsonify

from cinemas import get_content, parse_afisha_page, parse_kinopoisk_page, parse_imdb_page


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
URL_AFISHA = 'https://www.afisha.ru/spb/schedule_cinema/'
CACHE_AFISHA = {'threshold': 1, 'default_timeout': 60*60*1}
URL_KP = 'https://www.kinopoisk.ru/index.php'
CACHE_KP = {'threshold': 100, 'default_timeout': 60*60*24}
URL_IMDB = 'https://www.imdb.com/search/title/'
CACHE_IMDB = {'threshold': 100, 'default_timeout': 60*60*24}
MOVIES_COUNT = 24 # Use -1 for displaying all movies


def thread_kp_imdb_function(movie):
    payload_kp = {'kp_query': '{} {}'.format(movie['title'], movie['year'])}
    content_kp = get_content(URL_KP, payload_kp, CACHE_KP)
    kp_movie = parse_kinopoisk_page(content_kp, movie['year'])
    if kp_movie['title_eng'] == '':
        kp_movie['imdb'] = ''
    else:
        year = movie['year']
        payload_imdb = {'title': kp_movie['title_eng'], 'title_type': 'feature', 'release_date': f'{year},{year}'}
        content_imdb = get_content(URL_IMDB, payload_imdb, CACHE_IMDB)
        kp_movie.update(parse_imdb_page(content_imdb, movie['year']))
    return kp_movie


def films_list():
    payload_afisha = {'view': 'list'}
    content_afisha = get_content(URL_AFISHA, payload_afisha, CACHE_AFISHA)
    afisha_data = parse_afisha_page(content_afisha)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        kp_imdb_movie_data = executor.map(thread_kp_imdb_function, afisha_data)
    for afisha_movie, kp_imdb_movie in zip(afisha_data, list(kp_imdb_movie_data)):
        afisha_movie.update(kp_imdb_movie)
    movies = sorted(
        [movie for movie in afisha_data if movie['rating_kp']],
        key=lambda x: x['rating_kp'],
        reverse=True)
    return movies


@app.route('/')
def render_films_list():
    movies = []
    error = ''
    try:
        movies = films_list()[:MOVIES_COUNT]
    except requests.exceptions.Timeout as e:
        error = 'TimeoutError'
    except requests.exceptions.HTTPError as e:
        error = 'HTTPError'
    except requests.exceptions.ConnectionError as e:
        error = 'ConnectionError'
    except requests.exceptions.RequestException as e:
        error = 'Another Request Error'
    finally:
        return render_template('films_list.html', movies=movies, error=error)


@app.route('/api/', methods=['GET'])
def jsonify_films_list():
    return jsonify(films_list()[:MOVIES_COUNT])


if __name__ == "__main__":
    load_dotenv()
    host = os.environ.get('HOST')
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
