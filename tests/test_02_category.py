import pytest

from .common import auth_client, create_categories, create_users_api


class Test02CategoryAPI:

    @pytest.mark.django_db(transaction=True)
    def test_01_category_not_auth(self, client):
        response = client.get('/api/v1/categories/')
        assert response.status_code != 404, (
            'Page `/api/v1/categories/` not found, check this address in *urls.py*'
        )
        assert response.status_code == 200, (
            'Check that a GET request to `/api/v1/categories/` without an auth token returns status 200'
        )

    @pytest.mark.django_db(transaction=True)
    def test_02_category_admin(self, admin_client):
        data = {}
        response = admin_client.post('/api/v1/categories/', data=data)
        assert response.status_code == 400, (
            'Check that POSTing `/api/v1/categories/` with invalid data returns status 400'
        )
        data = {
            'name': 'Films',
            'slug': 'films'
        }
        response = admin_client.post('/api/v1/categories/', data=data)
        assert response.status_code == 201, (
            'Check that POSTing `/api/v1/categories/` with valid data returns status 201'
        )
        data = {
            'name': 'New films',
            'slug': 'films'
        }
        response = admin_client.post('/api/v1/categories/', data=data)
        assert response.status_code == 400, (
            'Check that a POST request to `/api/v1/categories/` cannot create 2 categories with the same `slug`'
        )
        data = {
            'name': 'Books',
            'slug': 'books'
        }
        response = admin_client.post('/api/v1/categories/', data=data)
        assert response.status_code == 201, (
            'Check that POSTing `/api/v1/categories/` with valid data returns status 201'
        )
        response = admin_client.get('/api/v1/categories/')
        assert response.status_code == 200, (
            'Check that a GET request to `/api/v1/categories/` returns status 200'
        )
        data = response.json()
        assert 'count' in data, (
            'Check that a GET request to `/api/v1/categories/` returns paginated data. '
            'Parameter `count` not found'
        )
        assert 'next' in data, (
            'Check that a GET request to `/api/v1/categories/` returns paginated data. '
            'Parameter `next` not found'
        )
        assert 'previous' in data, (
            'Check that a GET request to `/api/v1/categories/` returns paginated data. '
            'Parameter `previous` not found'
        )
        assert 'results' in data, (
            'Check that a GET request to `/api/v1/categories/` returns paginated data. '
            'Parameter `results` not found'
        )
        assert data['count'] == 2, (
            'Check that a GET request to `/api/v1/categories/` returns paginated data. '
            'The value of the `count` parameter is invalid'
        )
        assert type(data['results']) == list, (
            'Check that a GET request to `/api/v1/categories/` returns paginated data. '
            'The type of the `results` parameter must be a list'
        )
        assert len(data['results']) == 2, (
            'Check that a GET request to `/api/v1/categories/` returns paginated data. '
            'The value of the `results` parameter is invalid'
        )
        assert {'name': 'Books', 'slug': 'books'} in data['results'], (
            'Check that a GET request to `/api/v1/categories/` returns paginated data. '
            'The value of the `results` parameter is invalid'
        )
        response = admin_client.get('/api/v1/categories/?search=Books')
        data = response.json()
        assert len(data['results']) == 1, (
            'Check that GET requests to `/api/v1/categories/` are filtered by the category name search parameter'
        )

    @pytest.mark.django_db(transaction=True)
    def test_03_category_delete_admin(self, admin_client):
        create_categories(admin_client)
        response = admin_client.delete('/api/v1/categories/books/')
        assert response.status_code == 204, (
            'Check that DELETE request to `/api/v1/categories/{slug}/` returns status 204'
        )
        response = admin_client.get('/api/v1/categories/')
        test_data = response.json()['results']
        assert len(test_data) == 1, (
            'Check that the DELETE request to `/api/v1/categories/{slug}/` deletes the category '
        )
        response = admin_client.get('/api/v1/categories/books/')
        code = 405
        assert response.status_code == code, (
            'Check that GET request `/api/v1/categories/{slug}/` '
            f'return status {code}'
        )
        response = admin_client.patch('/api/v1/categories/books/')
        assert response.status_code == code, (
            'Check that on PATCH request `/api/v1/categories/{slug}/` '
            f'return status {code}'
        )

    def check_permissions(self, user, user_name, categories):
        client_user = auth_client(user)
        data = {
            'name': 'Music',
            'slug': 'music'
        }
        response = client_user.post('/api/v1/categories/', data=data)
        assert response.status_code == 403, (
            f'Check that when POSTing `/api/v1/categories/` '
            f'with auth token {user_name} returns status 403'
        )
        response = client_user.delete(f'/api/v1/categories/{categories[0]["slug"]}/')
        assert response.status_code == 403, (
            f'Check that on DELETE request `/api/v1/categories/{{slug}}/` '
            f'with auth token {user_name} returns status 403'
        )

    @pytest.mark.django_db(transaction=True)
    def test_04_category_check_permission_admin(self, client, admin_client):
        categories = create_categories(admin_client)
        data = {
            'name': 'Music',
            'slug': 'music'
        }
        response = client.post('/api/v1/categories/', data=data)
        assert response.status_code == 401, (
            'Check that when POSTing `/api/v1/categories/` '
            'no auth token returned status 401'
        )
        response = client.delete(f'/api/v1/categories/{categories[0]["slug"]}/')
        assert response.status_code == 401, (
            'Check that on DELETE request `/api/v1/categories/{{slug}}/` '
            'no auth token returned status 401'
        )
        user, moderator = create_users_api(admin_client)
        self.check_permissions(user, 'regular user', categories)
        self.check_permissions(moderator, 'moderator', categories)

    @pytest.mark.django_db(transaction=True)
    def test_05_category_create_user(self, user_client):
        url = '/api/v1/categories/'
        data = {
            'name': 'Anything else',
            'slug': 'something'
        }
        response = user_client.post(url, data=data)
        code = 403
        assert response.status_code == code, (
            f'Check that when POSTing a request to `{url}`, category creation is disabled for '
            f'user with role user'
        )

    @pytest.mark.django_db(transaction=True)
    def test_06_category_create_moderator(self, moderator_client):
        url = '/api/v1/categories/'
        data = {
            'name': 'Anything else',
            'slug': 'something'
        }
        response = moderator_client.post(url, data=data)
        code = 403
        assert response.status_code == code, (
            f'Check that when POSTing a request to `{url}`, category creation is disabled for '
            f'user with role moderator'
        )
