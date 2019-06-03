# Cinemas Site

[This site](https://afisha-movies-rating-schedule.herokuapp.com/) shows movies
in Saint Petersburg cinemas, sorted by [Kinopoisk](https://www.kinopoisk.ru/)
rating. Current schedule parses from [afisha.ru](https://www.afisha.ru/spb/schedule_cinema/?view=list). [API](https://afisha-movies-rating-schedule.herokuapp.com/api) also available.


# How to Install

Python 3.6 and libraries from **requirements.txt** should be installed.

```bash

$ pip install -r requirements.txt
```


# Quickstart

1. Run **server.py**.

```bash

$ python server.py

 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 * Restarting with inotify reloader
 * Debugger is active!

```

2. Goto [http://127.0.0.1:5000/ ](http://127.0.0.1:5000/ )


# How to Deploy

For example, you can deploy the site on [Heroku](https://heroku.com), with
GitHub integration.

1. Create a new app on Heroku with GitHub deployment method.

2. Do not forget about **Procfile**:

```bash

web: python3 server.py

```

3. Add your environment variables to Settings > Config Vars section (DEBUG and PORT).

4. Open https://[your-app-name].herokuapp.com/ in your browser

5. For reading logs install [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli#download-and-install).


# Project Goals

The code is written for educational purposes. Training course for web-developers - [DEVMAN.org](https://devman.org)
