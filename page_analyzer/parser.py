import requests
from bs4 import BeautifulSoup


def get_resp_data(url_name):
    resp = requests.get(url_name)
    status_code = resp.status_code

    if status_code != 200:
        raise requests.exceptions.RequestException

    html = resp.text
    soup = BeautifulSoup(html, features="html.parser")

    h1, title, description = None, None, None

    if soup.find('h1'):
        h1 = soup.find('h1').text.strip()

    if soup.find('title'):
        title = soup.find('title').text.strip()

    if soup.find('meta', {"name": "description"}):
        description = soup.find('meta', {"name": "description"})
        description = description.attrs['content']

    return status_code, h1, title, description