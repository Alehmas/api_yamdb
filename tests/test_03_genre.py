import pytest

from .common import auth_client, create_genre, create_users_api


class Test03GenreAPI:

    @pytest.mark.django_db(transaction=True)
    def test_01_genre_not_auth(self, client):
        response = client.get('/api/v1/genres/')
        assert response.status_code != 404, (
            'Page `/api/v1/genres/` not found, check this address in *urls.py*'
        )
        assert response.status_code == 200, (
            'Check that a GET request to `/api/v1/genres/` without an auth token returns status 200'
        )

    @pytest.mark.django_db(transaction=True)
    def test_02_genre(self, admin_client):
        data = {}
        response = admin_client.post('/api/v1/genres/', data=data)
        assert response.status_code == 400, (
            'Check that POSTing `/api/v1/genres/` with invalid data returns status 400'
        )
        data = {'name': 'Horror', 'slug': 'horror'}
        response = admin_client.post('/api/v1/genres/', data=data)
        assert response.status_code == 201, (
            'Check that POSTing `/api/v1/genres/` with valid data returns status 201'
        )
        data = {'name': 'Horror', 'slug': 'horror'}
        response = admin_client.post('/api/v1/genres/', data=data)
        assert response.status_code == 400, (
            'Check that a POST request to `/api/v1/genres/` cannot create 2 genres with the same `slug`'
        )
        data = {'name': 'Comedy', 'slug': 'comedy'}
        response = admin_client.post('/api/v1/genres/', data=data)
        assert response.status_code == 201, (
            'Check that POSTing `/api/v1/genres/` with valid data returns status 201'
        )
        response = admin_client.get('/api/v1/genres/')
        assert response.status_code == 200, (
            'Check that a GET request to `/api/v1/genres/` returns status 200'
        )
        data = response.json()
        assert 'count' in data, (
            'Check that GET request to `/api/v1/genres/` returns data with pagination. '
            'Parameter `count` not found'
        )
        assert 'next' in data, (
            'Check that GET request to `/api/v1/genres/` returns data with pagination. '
            'Parameter `next` not found'
        )
        assert 'previous' in data, (
            'Check that GET request to `/api/v1/genres/` returns data with pagination. '
            'Parameter `previous` not found'
        )
        assert 'results' in data, (
            'Check that GET request to `/api/v1/genres/` returns data with pagination. '
            'Parameter `results` not found'
        )
        assert data['count'] == 2, (
            'Check that GET request to `/api/v1/genres/` returns data with pagination. '
            'The value of the `count` parameter is invalid'
        )
        assert type(data['results']) == list, (
            'Check that GET request to `/api/v1/genres/` returns data with pagination. '
            'The type of the `results` parameter must be a list'
        )
        assert len(data['results']) == 2, (
            'Check that GET request to `/api/v1/genres/` returns data with pagination. '
            'The value of the `results` parameter is invalid'
        )
        assert {'name': 'Horror', 'slug': 'horror'} in data['results'], (
            'Check that GET request to `/api/v1/genres/` returns data with pagination. '
            'The value of the `results` parameter is invalid'
        )
        response = admin_client.get('/api/v1/genres/?search=Horror')
        data = response.json()
        assert len(data['results']) == 1, (
            'Check that GET requests to `/api/v1/genres/` are filtered by the genre name search parameter '
        )

    @pytest.mark.django_db(transaction=True)
    def test_03_genres_delete(self, admin_client):
        genres = create_genre(admin_client)
        response = admin_client.delete(f'/api/v1/genres/{genres[0]["slug"]}/')
        assert response.status_code == 204, (
            'Check that DELETE request to `/api/v1/genres/{slug}/` returns status 204'
        )
        response = admin_client.get('/api/v1/genres/')
        test_data = response.json()['results']
        assert len(test_data) == len(genres) - 1, (
            'Check that DELETE requesting `/api/v1/genres/{slug}/` deletes the genre '
        )
        response = admin_client.get(f'/api/v1/genres/{genres[0]["slug"]}/')
        assert response.status_code == 405, (
            'Check that a GET request to `/api/v1/genres/{slug}/` returns status 405'
        )
        response = admin_client.patch(f'/api/v1/genres/{genres[0]["slug"]}/')
        assert response.status_code == 405, (
            'Check that PATCH requesting `/api/v1/genres/{slug}/` returns status 405'
        )

    def check_permissions(self, user, user_name, genres):
        client_user = auth_client(user)
        data = {
            'name': 'Action',
            'slug': 'action'
        }
        response = client_user.post('/api/v1/genres/', data=data)
        assert response.status_code == 403, (
            f'Check that when POSTing `/api/v1/genres/` '
            f'with auth token {user_name} returns status 403'
        )
        response = client_user.delete(f'/api/v1/genres/{genres[0]["slug"]}/')
        assert response.status_code == 403, (
            f'Check that on DELETE request `/api/v1/genres/{{slug}}/` '
            f'with auth token {user_name} returns status 403'
        )

    @pytest.mark.django_db(transaction=True)
    def test_04_genres_check_permission(self, client, admin_client):
        genres = create_genre(admin_client)
        data = {
            'name': 'Action',
            'slug': 'action'
        }
        response = client.post('/api/v1/genres/', data=data)
        assert response.status_code == 401, (
            'Check that when POSTing `/api/v1/genres/` '
            'no auth token returned status 401'
        )
        response = client.delete(f'/api/v1/genres/{genres[0]["slug"]}/')
        assert response.status_code == 401, (
            'Check that on DELETE request `/api/v1/genres/{{slug}}/` '
            'no auth token returned status 401'
        )
        user, moderator = create_users_api(admin_client)
        self.check_permissions(user, 'ordinary user', genres)
        self.check_permissions(moderator, 'moderator', genres)

    @pytest.mark.django_db(transaction=True)
    def test_05_genre_create_user(self, user_client):
        url = '/api/v1/genres/'
        data = {
            'name': 'Anything else',
            'slug': 'something'
        }
        response = user_client.post(url, data=data)
        code = 403
        assert response.status_code == code, (
            f'Check that when POSTing a `{url}`, creating genres is not available for '
            f'user with role user'
        )

    @pytest.mark.django_db(transaction=True)
    def test_06_genre_create_moderator(self, moderator_client):
        url = '/api/v1/genres/'
        data = {
            'name': 'Anything else',
            'slug': 'something'
        }
        response = moderator_client.post(url, data=data)
        code = 403
        assert response.status_code == code, (
            f'Check that when POSTing a `{url}`, creating genres is not available for '
            f'user with role moderator'
        )
