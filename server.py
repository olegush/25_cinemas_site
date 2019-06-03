import os
import time

import concurrent.futures

from flask import Flask, render_template, jsonify

from cinemas import get_content, parse_afisha_page, parse_kinopoisk_page


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
CACHE_AFISHA = {'threshold': 1, 'default_timeout': 60*60*1}
CACHE_KINOPOISK = {'threshold': 100, 'default_timeout': 60*60*24}
MOVIES_COUNT = 12


def thread_kinopoisk_function(movie):
    url = 'https://www.kinopoisk.ru/index.php'
    payload = {'kp_query': '{} {}'.format(movie['title'], movie['year'])}
    content = get_content(url, payload, CACHE_KINOPOISK)
    movie['rating'], movie['id_kinopoisk'] = parse_kinopoisk_page(
                                                content,
                                                movie['year'])


def films_list():
    payload_afisha = {'view': 'list'}
    url_afisha = 'https://www.afisha.ru/spb/schedule_cinema/'
    content_afisha = get_content(url_afisha, payload_afisha, CACHE_AFISHA)
    movies = parse_afisha_page(content_afisha)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(thread_kinopoisk_function, movies)

    movies = sorted(
        movies,
        key=lambda x: x['rating'] if x['rating'] else 0,
        reverse=True)
    return movies


@app.route('/')
def render_films_list():
    return render_template('films_list.html', movies=films_list()[:MOVIES_COUNT])


@app.route('/api/', methods=['GET'])
def jsonify_films_list():
    return jsonify(films_list()[:MOVIES_COUNT])


if __name__ == "__main__":
    app.debug = os.environ['DEBUG']
    app.run()
