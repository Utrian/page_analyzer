import os
import requests
import psycopg2
from datetime import date
from bs4 import BeautifulSoup
from psycopg2.extras import NamedTupleCursor


class Database:
    def __init__(self):
        self.DATABASE_URL = os.getenv('DATABASE_URL')
        self.conn = psycopg2.connect(self.DATABASE_URL)

    def save(self):
        self.conn.commit()

    def close(self):
        self.conn.close()


class Urls(Database):
    def get_urls_data(self) -> NamedTupleCursor:
        with self.conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            curs.execute(
                'SELECT DISTINCT ON (urls.id)'
                'urls.id, urls.name, url_checks.status_code, '
                'MAX(url_checks.created_at) as last_check '
                'FROM urls LEFT JOIN url_checks '
                'ON urls.id = url_checks.url_id '
                'GROUP BY urls.id, url_checks.status_code '
                'ORDER BY urls.id DESC;'
            )
            urls_data = curs.fetchall()

        return urls_data

    def find_url_by_id(self, id: int) -> NamedTupleCursor:
        with self.conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            curs.execute('SELECT * FROM urls WHERE id=(%s)', (id,))
            return curs.fetchone()

    def find_url_by_name(self, url: str) -> NamedTupleCursor:
        with self.conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            curs.execute('SELECT * FROM urls WHERE name=(%s)', (url,))
            return curs.fetchone()

    def create_url_entry(self, url_name: str):
        with self.conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            curs.execute(
                'INSERT INTO urls (name, created_at) VALUES (%s, %s)',
                (url_name, date.today())
            )

        self.save()
        return self.find_url_by_name(url_name)


def get_resp_data(url_name):
    resp = requests.get(url_name)
    status_code = resp.status_code

    if status_code != 200:
        raise requests.exceptions.RequestException

    html = resp.text
    soup = BeautifulSoup(html, features="html.parser")

    h1, title, description = None, None, None

    if soup.select('h1'):
        h1 = soup.select('h1')[0].text.strip()

    if soup.select('title'):
        title = soup.select('title')[0].text.strip()

    if soup.find('meta', {"name": "description"}):
        description = soup.find('meta', {"name": "description"})
        description = description.attrs['content']

    return status_code, h1, title, description


class Checks(Database):
    def find_checks(self, url_id: int) -> NamedTupleCursor:
        with self.conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            curs.execute(
                'SELECT * FROM url_checks '
                'WHERE url_id=%s ORDER BY id DESC',
                (url_id,)
            )
            checks_data = curs.fetchall()

        return checks_data

    def create_check_entry(self, url_id: int):
        with self.conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            curs.execute(
                'SELECT name FROM urls WHERE id=%s',
                (url_id,)
            )
            url_name = curs.fetchone().name

        status_code, h1, title, description = get_resp_data(url_name)

        with self.conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            curs.execute(
                'INSERT INTO url_checks '
                '('
                'url_id, status_code, h1, '
                'title, description, created_at'
                ') '
                'VALUES (%s, %s, %s, %s, %s, %s)',
                (url_id, status_code, h1, title, description, date.today())
            )

        self.save()
