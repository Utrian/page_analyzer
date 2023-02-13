import os
import psycopg2
import requests
import validators
from urllib.parse import urlparse
from dotenv import load_dotenv
from flask import (
    Flask, render_template, request,
    redirect, url_for, flash, get_flashed_messages
)

from .database import Urls, Checks


app = Flask(__name__)

load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def homepage():
    message = get_flashed_messages(with_categories=True)
    return render_template('index.html', message=message)


@app.get('/urls')
def show_all_urls():
    try:
        db = Urls()
        urls_data = db.get_urls_data()
        db.close()

        return render_template(
            'urls.html', urls=urls_data
        )

    except psycopg2.DatabaseError:
        flash('Не удалось подключиться к базе данных', 'alert-warning')
        return redirect(url_for('homepage'))


@app.post('/urls')
def new_url():
    url = urlparse(request.form.get('url'))
    norm_url = url.scheme + '://' + url.netloc

    if not validators.url(norm_url) or len(norm_url) > 255:
        flash('Некорректный URL', 'alert-danger')

        return render_template(
            'index.html',
            message=get_flashed_messages(with_categories=True)
        ), 422

    try:
        db = Urls()
        url_data = db.find_url(norm_url)

        if url_data:
            flash('Страница уже существует', 'alert-info')
        else:
            url_data = db.create_url_entry(norm_url)
            flash('Страница успешно добавлена', 'alert-success')

        db.close()
        return redirect(url_for('show_url', id=url_data.id))

    except psycopg2.DatabaseError:
        flash('Не удалось подключиться к базе данных', 'alert-warning')
        return redirect(url_for('homepage'))


@app.get('/urls/<int:id>')
def show_url(id):
    try:
        db = Urls()
        url_data = db.find_url(id)
        checks_data = Checks.find_checks(db, id)
        db.close()

        message = get_flashed_messages(with_categories=True)
        return render_template(
            'show_url.html', url=url_data,
            url_checks=checks_data, message=message
        )

    except psycopg2.DatabaseError:
        flash('Не удалось подключиться к базе данных', 'alert-warning')
        return redirect(url_for('homepage'))


@app.post('/urls/<int:id>/check')
def check_url(id):
    try:
        db = Checks()
        db.create_check_entry(id)
        db.close()

        flash('Страница успешно проверена', 'alert-success')
        return redirect(url_for('show_url', id=id))

    except psycopg2.DatabaseError:
        flash('Не удалось подключиться к базе данных', 'alert-warning')
        return redirect(url_for('homepage'))

    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'alert-danger')
        return redirect(url_for('show_url', id=id))
