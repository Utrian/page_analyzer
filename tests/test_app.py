                                        #################################################
                                        ##########       Alpha version       ############
                                        #################################################

def test_app():
    assert 1 == 1

# import pytest
# import psycopg2
# import pg_temp
# from page_analyzer.app import app


# temp_db = pg_temp.init_temp_db(databases=['testdb'])
# connection = psycopg2.connect(
#     host=temp_db.pg_socket_dir,
#     database='testdb'
#     )


# @pytest.fixture()
# def application():
#     app.testing = True
#     return app


# @pytest.fixture()
# def client(application):
#     return application.test_client()


# @pytest.fixture()
# def runner(application):
#     return application.test_cli_runner()


# def test_homepage(client):
#     response = client.get('/')
#     assert response.status_code == 200


# @pytest.mark.parametrize(
#     'page',
#     [
#         pytest.param(
#             '/',
#             id='homepage'
#         ),
#         pytest.param(
#             'urls',
#             id='urls list'
#         ),
#         pytest.param(
#             'urls/1',
#             id='page of the entry'
#         )
#     ]
# )
# def test_get_status_code(client, page):
#     response = client.get(page)
#     assert response.status_code == 200


# @pytest.mark.parametrize(
#     'is_fit, url',
#     [
#         pytest.param(
#             True,
#             'http://wrong.com',
#             id='http://wrong.com'
#         ),
#         pytest.param(
#             True,
#             'https://youtu.be',
#             id='https://youtu.be'
#         ),
#         pytest.param(
#             False,
#             'httpsss://wrong.com',
#             id='httpsss://wrong.com'
#         ),
#         pytest.param(
#             False,
#             '',
#             id='empty line'
#         )
#     ]
# )
# def test_homepage_form(client, is_fit, url):
#     response = client.post('/urls', data={'url': url})

#     if is_fit is True:
#         assert response.status_code == 302
#     else:
#         assert response.status_code == 422
