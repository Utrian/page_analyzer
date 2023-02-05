import os
import psycopg2
import requests
import validators.url
from typing import Union
from datetime import date
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from psycopg2.extras import NamedTupleCursor
from dotenv import load_dotenv
from flask import (
    Flask, render_template, request,
    redirect, url_for, flash, get_flashed_messages
)


app = Flask(__name__)

load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


class Database:
    def __init__(self):
        self.DATABASE_URL = os.getenv('DATABASE_URL')
        self.conn = psycopg2.connect(self.DATABASE_URL)
        self.curs = self.conn.cursor(cursor_factory=NamedTupleCursor)

    def save(self):
        self.conn.commit()

    def close(self):
        self.curs.close()
        self.conn.close()

    def get_urls_data(self) -> NamedTupleCursor:
        self.curs.execute(
            'SELECT DISTINCT ON (urls.id)'
            'urls.id, urls.name, url_checks.status_code, '
            'MAX(url_checks.created_at) as last_check '
            'FROM urls LEFT JOIN url_checks '
            'ON urls.id = url_checks.url_id '
            'GROUP BY urls.id, url_checks.status_code '
            'ORDER BY urls.id DESC;'
        )
        urls_data = self.curs.fetchall()
        return urls_data

    def find_url(self, url: Union[str, int]) -> NamedTupleCursor:
        if isinstance(url, str):
            self.curs.execute('SELECT * FROM urls WHERE name=%s', (url,))
        else:
            id = url
            self.curs.execute('SELECT * FROM urls WHERE id=%s', (id,))
        url_data = self.curs.fetchone()
        return url_data

    def create_url_entry(self, url_name: str):
        self.curs.execute(
            'INSERT INTO urls (name, created_at) VALUES (%s, %s)',
            (url_name, date.today())
        )
        self.save()
        return self.find_url(url_name)

    def find_checks(self, url_id: int) -> NamedTupleCursor:
        self.curs.execute(
            'SELECT * FROM url_checks WHERE url_id=%s ORDER BY id DESC',
            (url_id,)
        )
        checks_data = self.curs.fetchall()
        return checks_data

    def create_check_entry(self, url_id: int):
        h1, title, description = None, None, None

        self.curs.execute(
            'SELECT name FROM urls WHERE id=%s',
            (url_id,)
        )
        url_name = self.curs.fetchone().name

        resp = requests.get(url_name)
        status_code = resp.status_code

        html = resp.text
        soup = BeautifulSoup(html)

        if soup.select('h1'):
            h1 = soup.select('h1')[0].text.strip()

        if soup.select('title'):
            title = soup.select('title')[0].text.strip()

        if soup.find('meta', {"name": "description"}):
            description = soup.find('meta', {"name": "description"})
            description = description.attrs['content']

        self.curs.execute(
            'INSERT INTO url_checks '
            '(url_id, status_code, h1, title, description, created_at) '
            'VALUES (%s, %s, %s, %s, %s, %s)',
            (url_id, status_code, h1, title, description, date.today())
        )
        self.save()


@app.route('/')
def homepage():
    message = get_flashed_messages(with_categories=True)
    return render_template('index.html', message=message)


@app.get('/urls')
def show_all_urls():
    try:
        db = Database()
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
    url_name = url.scheme + '://' + url.netloc

    if not (len(url_name) <= 255 and validators.url(url_name)):
        flash('Некорректный URL', 'alert-danger')
        return redirect(url_for('homepage'))

    try:
        db = Database()
        url_data = db.find_url(url_name)

        if url_data:
            flash('Страница уже существует', 'alert-info')
        else:
            url_data = db.create_url_entry(url_name)
            flash('Страница успешно добавлена', 'alert-success')

        db.close()
        return redirect(url_for('show_url', id=url_data.id))

    except psycopg2.DatabaseError:
        flash('Не удалось подключиться к базе данных', 'alert-warning')
        return redirect(url_for('homepage'))


@app.get('/urls/<int:id>')
def show_url(id):
    try:
        db = Database()
        url_data = db.find_url(id)
        checks_data = db.find_checks(id)
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
        db = Database()
        db.create_check_entry(id)
        db.close()

        flash('Страница успешно проверена', 'alert-success')
        return redirect(url_for('show_url', id=id))

    except psycopg2.DatabaseError:
        flash('Не удалось подключиться к базе данных', 'alert-warning')
        return redirect(url_for('homepage'))