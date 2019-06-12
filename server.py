import os

import requests
from dotenv import load_dotenv
import concurrent.futures
from flask import Flask, render_template, jsonify

from cinemas import get_content, parse_afisha_page, parse_kinopoisk_page


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
CACHE_AFISHA = {'threshold': 1, 'default_timeout': 60*60*1}
CACHE_KINOPOISK = {'threshold': 100, 'default_timeout': 60*60*24}
MOVIES_COUNT = 12 # Use -1 for displaying all movies


def thread_kinopoisk_function(movie):
    url = 'https://www.kinopoisk.ru/index.php'
    payload = {'kp_query': '{} {}'.format(movie['title'], movie['year'])}
    content = get_content(url, payload, CACHE_KINOPOISK)
    return parse_kinopoisk_page(content, movie['year'])


def films_list():
    payload_afisha = {'view': 'list'}
    url_afisha = 'https://www.afisha.ru/spb/schedule_cinema/'
    content_afisha = get_content(url_afisha, payload_afisha, CACHE_AFISHA)
    afisha_data = parse_afisha_page(content_afisha)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        kinopoisk_data = executor.map(thread_kinopoisk_function, afisha_data)
    for afisha_movie, kinopoisk_movie in zip(afisha_data, list(kinopoisk_data)):
        afisha_movie.update(kinopoisk_movie)
    movies = sorted(
        afisha_data,
        key=lambda x: x['rating'] if x['rating'] else 0,
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
    app.run(port=int(os.environ['PORT']))
