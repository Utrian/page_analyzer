import os
import psycopg2
import validators
from urllib.parse import urlparse
from dotenv import load_dotenv
from flask import (
    Flask, render_template, request,
    redirect, url_for, flash
)

from .parser import get_check_data
from .database import Urls, Checks, Database


app = Flask(__name__)

load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def homepage():
    return render_template('index.html')


@app.get('/urls')
def show_all_urls():
    try:
        with Urls() as db:
            urls_data = db.get_urls_data()

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
        return render_template('index.html'), 422

    try:
        with Urls() as db:
            url_data = db.find_url_by_name(norm_url)

            if url_data:
                url_id = url_data.id
                flash('Страница уже существует', 'alert-info')
            else:
                url_id = db.create_url_entry(norm_url)
                flash('Страница успешно добавлена', 'alert-success')

        return redirect(url_for('show_url', id=url_id))

    except psycopg2.DatabaseError:
        flash('Не удалось подключиться к базе данных', 'alert-warning')
        return redirect(url_for('homepage'))


@app.get('/urls/<int:id>')
def show_url(id):
    try:
        with Urls() as db:
            url_data = db.find_url_by_id(id)
            checks_data = Checks.find_checks(db, id)

        return render_template(
            'show_url.html', url=url_data,
            url_checks=checks_data
        )

    except psycopg2.DatabaseError:
        flash('Не удалось подключиться к базе данных', 'alert-warning')
        return redirect(url_for('homepage'))


@app.post('/urls/<int:id>/check')
def check_url(id):
    try:
        with Database() as db:
            url_name = Urls.find_url_by_id(db, id).name
            check_data = get_check_data(id, url_name)
            Checks.create_check_entry(db, check_data)

        flash('Страница успешно проверена', 'alert-success')
        return redirect(url_for('show_url', id=id))

    except psycopg2.DatabaseError:
        flash('Не удалось подключиться к базе данных', 'alert-warning')
        return redirect(url_for('homepage'))

    except Exception:
        flash('Произошла ошибка при проверке', 'alert-danger')
        return redirect(url_for('show_url', id=id))
