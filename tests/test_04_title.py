import pytest

from .common import (auth_client, create_categories, create_genre,
                     create_titles, create_users_api)


class Test04TitleAPI:

    @pytest.mark.django_db(transaction=True)
    def test_01_title_not_auth(self, client):
        response = client.get('/api/v1/titles/')
        assert response.status_code != 404, (
            'Page `/api/v1/titles/` not found, check this address in *urls.py*'
        )
        assert response.status_code == 200, (
            'Check that a GET request to `/api/v1/titles/` without an auth token returns status 200'
        )

    @pytest.mark.django_db(transaction=True)
    def test_02_title_admin(self, admin_client):
        genres = create_genre(admin_client)
        categories = create_categories(admin_client)
        data = {}
        response = admin_client.post('/api/v1/titles/', data=data)
        assert response.status_code == 400, (
            'Check that POSTing `/api/v1/titles/` with invalid data returns status 400'
        )
        data = {'name': 'Turn there', 'year': 2000, 'genre': [genres[0]['slug'], genres[1]['slug']],
                'category': categories[0]['slug'], 'description': 'Cool dive'}
        response = admin_client.post('/api/v1/titles/', data=data)
        assert response.status_code == 201, (
            'Check that POSTing `/api/v1/titles/` with valid data returns status 201'
        )
        data = {'name': 'Project', 'year': 2020, 'genre': [genres[2]['slug']], 'category': categories[1]['slug'],
                'description': 'Main Drama of the Year'}
        response = admin_client.post('/api/v1/titles/', data=data)
        assert response.status_code == 201, (
            'Check that POSTing `/api/v1/titles/` with valid data returns status 201'
        )
        assert type(response.json().get('id')) == int, (
            'Check that when you POST a request to `/api/v1/titles/` you return the data of the created object. '
            'Value `id` is not present or is not an integer.'
        )
        response = admin_client.get('/api/v1/titles/')
        assert response.status_code == 200, (
            'Check that GET request `/api/v1/titles/` returns status 200'
        )
        data = response.json()
        assert 'count' in data, (
            'Check that GET request to `/api/v1/titles/` returns data with pagination. '
            'Parameter `count` not found'
        )
        assert 'next' in data, (
            'Check that GET request to `/api/v1/titles/` returns data with pagination. '
            'Parameter `next` not found'
        )
        assert 'previous' in data, (
            'Check that GET request to `/api/v1/titles/` returns data with pagination. '
            'Parameter `previous` not found'
        )
        assert 'results' in data, (
            'Check that GET request to `/api/v1/titles/` returns data with pagination. '
            'Parameter `results` not found'
        )
        assert data['count'] == 2, (
            'Check that GET request to `/api/v1/titles/` returns data with pagination. '
            'The value of the `count` parameter is invalid'
        )
        assert type(data['results']) == list, (
            'Check that GET request to `/api/v1/titles/` returns data with pagination. '
            'The type of the `results` parameter must be a list'
        )
        assert len(data['results']) == 2, (
            'Check that GET request to `/api/v1/titles/` returns data with pagination. '
            'The value of the `results` parameter is invalid'
        )
        if data['results'][0].get('name') == 'Turn there':
            title = data['results'][0]
        elif data['results'][1].get('name') == 'Turn there':
            title = data['results'][1]
        else:
            assert False, (
                'Check that GET request to `/api/v1/titles/` returns data with pagination. '
                'The value of the `results` parameter is invalid, `name` was not found or was not saved in the POST request.'
            )

        assert title.get('rating') is None, (
            'Check that GET request to `/api/v1/titles/` returns data with pagination. '
            'The value of the `results` parameter is invalid, `rating` without reviews must be `None`'
        )
        assert title.get('category') == categories[0], (
            'Check that GET request to `/api/v1/titles/` returns data with pagination. '
            'The value of the `results` parameter is invalid, the value of `category` is invalid '
            'or was not saved in the POST request.'
        )
        assert genres[0] in title.get('genre', []) and genres[1] in title.get('genre', []), (
            'Check that GET request to `/api/v1/titles/` returns data with pagination. '
            'The value of the `results` parameter is invalid, the value of `genre` is invalid '
            'or was not saved in the POST request.'
        )
        assert title.get('year') == 2000, (
            'Check that GET request to `/api/v1/titles/` returns data with pagination. '
            'The value of the parameter `results` is invalid, the value of `year` is invalid '
            'or was not saved in the POST request.'
        )
        assert title.get('description') == 'Cool dive', (
            'Check that GET request to `/api/v1/titles/` returns data with pagination. '
            'The value of the `results` parameter is invalid, the value of `description` is invalid '
            'or was not saved in the POST request.'
        )
        assert type(title.get('id')) == int, (
            'Check that GET request to `/api/v1/titles/` returns data with pagination. '
            'The value of the `results` parameter is invalid, the value of `id` is not present or is not an integer.'
        )
        data = {'name': 'Turn', 'year': 2020, 'genre': [genres[1]['slug']],
                'category': categories[1]['slug'], 'description': 'Cool dive'}
        admin_client.post('/api/v1/titles/', data=data)
        response = admin_client.get(f'/api/v1/titles/?genre={genres[1]["slug"]}')
        data = response.json()
        assert len(data['results']) == 2, (
            'Check that GET requests to `/api/v1/titles/` are filtered by the `genre` `slug` parameter of the genre'
        )
        response = admin_client.get(f'/api/v1/titles/?category={categories[0]["slug"]}')
        data = response.json()
        assert len(data['results']) == 1, (
            'Check that GET request `/api/v1/titles/` is filtered by `category` parameter `slug` category'
        )
        response = admin_client.get('/api/v1/titles/?year=2000')
        data = response.json()
        assert len(data['results']) == 1, (
            'Check that GET request `/api/v1/titles/` is filtered by `year` year parameter'
        )
        response = admin_client.get('/api/v1/titles/?name=Turn')
        data = response.json()
        assert len(data['results']) == 2, (
            'Check that GET request `/api/v1/titles/` is filtered by `name` title parameter'
        )
        invalid_data = {
            'name': 'Turn', 'year': 'two thousand six', 'genre': [genres[1]['slug']],
            'category': categories[1]['slug'], 'description': 'Cool dive'
        }
        response = admin_client.post('/api/v1/titles/', data=invalid_data)
        code = 400
        assert response.status_code == code, (
            'Check that when POSTing `/api/v1/titles/`, the year field is validated '
            'and when passing an invalid value, status 400 is returned'
        )

    @pytest.mark.django_db(transaction=True)
    def test_03_titles_detail(self, client, admin_client):
        titles, categories, genres = create_titles(admin_client)
        response = client.get(f'/api/v1/titles/{titles[0]["id"]}/')
        assert response.status_code != 404, (
            'Page `/api/v1/titles/{title_id}/` not found, check this address in *urls.py*'
        )
        assert response.status_code == 200, (
            'Check that GET request `/api/v1/titles/{title_id}/` '
            'without authorization token returns status 200'
        )
        data = response.json()
        assert type(data.get('id')) == int, (
            'Check that a GET request to `/api/v1/titles/{title_id}/` returns object data. '
            'Value `id` is not present or is not an integer.'
        )
        assert data.get('category') == categories[0], (
            'Check that a GET request to `/api/v1/titles/{title_id}/` returns object data. '
            'The value of `category` is invalid.'
        )
        assert data.get('name') == titles[0]['name'], (
            'Check that a GET request to `/api/v1/titles/{title_id}/` returns object data. '
            'The value of `name` is invalid.'
        )
        data = {
            'name': 'New name',
            'category': categories[1]['slug']
        }
        response = admin_client.patch(f'/api/v1/titles/{titles[0]["id"]}/', data=data)
        assert response.status_code == 200, (
            'Check that PATCH requesting `/api/v1/titles/{title_id}/` returns status 200'
        )
        data = response.json()
        assert data.get('name') == 'New name', (
            'Check that PATCH requesting `/api/v1/titles/{title_id}/` returns object data. '
            'The value of `name` has been changed.'
        )
        response = admin_client.get(f'/api/v1/titles/{titles[0]["id"]}/')
        assert response.status_code == 200, (
            'Check that GET request `/api/v1/titles/{title_id}/` '
            'without authorization token returns status 200'
        )
        data = response.json()
        assert data.get('category') == categories[1], (
            'Check that you change the value of `category` when you PATCH `/api/v1/titles/{title_id}/`.'
        )
        assert data.get('name') == 'New name', (
            'Check that when you PATCH a request to `/api/v1/titles/{title_id}/` you change the value of `name`.'
        )

        response = admin_client.delete(f'/api/v1/titles/{titles[0]["id"]}/')
        assert response.status_code == 204, (
            'Check that DELETE request `/api/v1/titles/{title_id}/` returns status 204'
        )
        response = admin_client.get('/api/v1/titles/')
        test_data = response.json()['results']
        assert len(test_data) == len(titles) - 1, (
            'Check that when you DELETE request `/api/v1/titles/{title_id}/` you are deleting the object'
        )

    def check_permissions(self, user, user_name, titles, categories, genres):
        client_user = auth_client(user)
        data = {'name': 'Miracle Yudo', 'year': 1999, 'genre': [genres[2]['slug'], genres[1]['slug']],
                'category': categories[0]['slug'], 'description': 'Boom'}
        response = client_user.post('/api/v1/titles/', data=data)
        assert response.status_code == 403, (
            f'Check that when POSTing `/api/v1/titles/` '
            f'with auth token {user_name} returns status 403'
        )
        response = client_user.patch(f'/api/v1/titles/{titles[0]["id"]}/', data=data)
        assert response.status_code == 403, (
           f'Check that on PATCH request `/api/v1/titles/{{title_id}}/` '
            f'with auth token {user_name} returns status 403'
        )
        response = client_user.delete(f'/api/v1/titles/{titles[0]["id"]}/')
        assert response.status_code == 403, (
            f'Check that on DELETE request `/api/v1/titles/{{title_id}}/` '
            f'with auth token {user_name} returns status 403'
        )

    @pytest.mark.django_db(transaction=True)
    def test_04_titles_check_permission(self, client, admin_client):
        titles, categories, genres = create_titles(admin_client)
        data = {'name': 'Miracle Yudo', 'year': 1999, 'genre': [genres[2]['slug'], genres[1]['slug']],
                'category': categories[0]['slug'], 'description': 'Boom'}
        response = client.post('/api/v1/titles/', data=data)
        assert response.status_code == 401, (
            'Check that when POSTing `/api/v1/titles/` '
            'no auth token returned status 401'
        )
        response = client.patch(f'/api/v1/titles/{titles[0]["id"]}/', data=data)
        assert response.status_code == 401, (
            'Check that on PATCH request `/api/v1/titles/{{title_id}}/` '
            'no auth token returned status 401'
        )
        response = client.delete(f'/api/v1/titles/{titles[0]["id"]}/')
        assert response.status_code == 401, (
            'Check that on DELETE request `/api/v1/titles/{{title_id}}/` '
            'no auth token returned status 401'
        )
        user, moderator = create_users_api(admin_client)
        self.check_permissions(user, 'regular user', titles, categories, genres)
        self.check_permissions(moderator, 'moderator', titles, categories, genres)
