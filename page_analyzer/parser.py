import requests
from bs4 import BeautifulSoup


def get_check_data(url_id, url_name):
    resp = requests.get(url_name)
    status_code = resp.status_code

    html = resp.text
    soup = BeautifulSoup(html, features="html.parser")

    h1, title, description = None, None, None

    if soup.find('h1'):
        h1 = soup.find('h1').get_text(strip=True)

    if soup.find('title'):
        title = soup.find('title').get_text(strip=True)

    if soup.find('meta', {"name": "description"}):
        description = soup.find(
            'meta', {"name": "description"}
            ).get('content')

    return {
        'id': url_id,
        'status_code': status_code,
        'h1': h1, 'title': title,
        'description': description
    }
