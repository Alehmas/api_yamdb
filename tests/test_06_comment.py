import pytest

from .common import auth_client, create_comments, create_reviews


class Test06CommentAPI:

    @pytest.mark.django_db(transaction=True)
    def test_01_comment_not_auth(self, client, admin_client, admin):
        reviews, titles, _, _ = create_reviews(admin_client, admin)
        response = client.get(f'/api/v1/titles/{titles[0]["id"]}/reviews/{reviews[0]["id"]}/comments/')
        assert response.status_code != 404, (
            'Page `/api/v1/titles/{title_id}/reviews/{review_id}/comments/` '
            'not found, check this address in *urls.py*'
        )
        assert response.status_code == 200, (
            'Check that on GET request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/` '
            'without authorization token returns status 200'
        )

    def create_comment(self, client_user, title_id, review_id, text):
        data = {'text': text}
        response = client_user.post(f'/api/v1/titles/{title_id}/reviews/{review_id}/comments/', data=data)
        assert response.status_code == 201, (
            'Check that when POSTing `/api/v1/titles/{title_id}/reviews/{review_id}/comments/` '
            'with correct data returns status 201, api is available to any authenticated user'
        )
        return response

    @pytest.mark.django_db(transaction=True)
    def test_02_comment(self, admin_client, admin):
        reviews, titles, user, moderator = create_reviews(admin_client, admin)
        client_user = auth_client(user)
        client_moderator = auth_client(moderator)
        data = {}
        response = admin_client.post(
            f'/api/v1/titles/{titles[0]["id"]}/reviews/{reviews[0]["id"]}/comments/', data=data
        )
        assert response.status_code == 400, (
            'Check that when POSTing `/api/v1/titles/{title_id}/reviews/{review_id}/comments/` '
            'with invalid data returns status 400'
        )
        self.create_comment(admin_client, titles[0]["id"], reviews[0]["id"], 'qwerty')
        self.create_comment(client_user, titles[0]["id"], reviews[0]["id"], 'qwerty123')
        self.create_comment(client_moderator, titles[0]["id"], reviews[0]["id"], 'qwerty321')

        self.create_comment(admin_client, titles[0]["id"], reviews[1]["id"], 'qwerty432')
        self.create_comment(client_user, titles[0]["id"], reviews[1]["id"], 'qwerty534')
        response = self.create_comment(client_moderator, titles[0]["id"], reviews[1]["id"], 'qwerty231')

        assert type(response.json().get('id')) == int, (
            'Check that when POSTing `/api/v1/titles/{title_id}/reviews/{review_id}/comments/` '
            'return the data of the created object. The value of `id` is not present or is not an integer.'
        )

        data = {'text': 'kjdfg'}
        response = admin_client.post('/api/v1/titles/999/reviews/999/comments/', data=data)
        assert response.status_code == 404, (
            'Check that when POSTing `/api/v1/titles/{title_id}/reviews/{review_id}/comments/` '
            'with a non-existent title_id or review_id, a 404 status is returned.'
        )
        data = {'text': 'asdf'}
        response = admin_client.post(
            f'/api/v1/titles/{titles[0]["id"]}/reviews/{reviews[0]["id"]}/comments/', data=data
        )
        assert response.status_code == 201, (
            'Check that when POSTing `/api/v1/titles/{title_id}/reviews/{review_id}/comments/` '
            'You can leave multiple comments on a review.'
        )

        response = admin_client.get(f'/api/v1/titles/{titles[0]["id"]}/reviews/{reviews[0]["id"]}/comments/')
        assert response.status_code == 200, (
            'Check that on GET request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/` '
            'return status 200'
        )
        data = response.json()
        assert 'count' in data, (
            'Check that on GET request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/` '
            'return data with pagination. `count` parameter not found'
        )
        assert 'next' in data, (
            'Check that on GET request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/` '
            'return data with pagination. `next` parameter not found'
        )
        assert 'previous' in data, (
            'Check that on GET request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/` '
            'return data with pagination. `previous` parameter not found'
        )
        assert 'results' in data, (
            'Check that on GET request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/` '
            'return data with pagination. `results` parameter not found'
        )
        assert data['count'] == 4, (
            'Check that on GET request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/` '
            'return data with pagination. The value of the `count` parameter is invalid'
        )
        assert type(data['results']) == list, (
            'Check that on GET request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/` '
            'return data with pagination. The type of the `results` parameter must be a list'
        )
        assert len(data['results']) == 4, (
            'Check that on GET request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/` '
            'return data with pagination. The value of the `results` parameter is invalid'
        )

        comment = None
        for item in data['results']:
            if item.get('text') == 'qwerty':
                comment = item
        assert comment, (
            'Check that on GET request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/` '
            'return data with pagination. The value of the `results` parameter is invalid, '
            '`text` not found or not saved on POST request.'
        )
        assert comment.get('author') == admin.username, (
            'Check that on GET request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/` '
            'return data with pagination. '
            'The value of the `results` parameter is invalid, `author` was not found or was not saved in the POST request.'
        )
        assert comment.get('pub_date'), (
            'Check that on GET request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/`'
            ' return data with pagination. The value of the `results` parameter is invalid, `pub_date` not found.'
        )
        assert type(comment.get('id')) == int, (
            'Check that on GET request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/` '
            'return data with pagination. '
            'The value of the `results` parameter is invalid, the value of `id` is not present or is not an integer.'
        )

    @pytest.mark.django_db(transaction=True)
    def test_03_review_detail(self, client, admin_client, admin):
        comments, reviews, titles, user, moderator = create_comments(admin_client, admin)
        pre_url = f'/api/v1/titles/{titles[0]["id"]}/reviews/{reviews[0]["id"]}/comments/'
        response = client.get(f'{pre_url}{comments[0]["id"]}/')
        assert response.status_code != 404, (
            'Page `/api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/` '
            'not found, check this address in *urls.py*'
        )
        assert response.status_code == 200, (
            'Check that on GET request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/` '
            'without authorization token returns status 200'
        )
        data = response.json()
        assert type(data.get('id')) == int, (
            'Check that on GET request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/` '
            'return object data. The value of `id` is not present or is not an integer.'
        )
        assert data.get('text') == reviews[0]['text'], (
            'Check that on GET request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/` '
            'return object data. The value of `text` is invalid.'
        )
        assert data.get('author') == reviews[0]['author'], (
            'Check that on GET request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/` '
            'return object data. The value of `author` is invalid.'
        )

        data = {'text': 'rewq'}
        response = admin_client.patch(f'{pre_url}{comments[0]["id"]}/', data=data)
        assert response.status_code == 200, (
            'Check that on PATCH request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/` '
            'returning status 200'
        )
        data = response.json()
        assert data.get('text') == 'rewq', (
            'Check that on PATCH request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/` '
            'return object data. The value of `text` has been changed.'
        )
        response = admin_client.get(f'{pre_url}{comments[0]["id"]}/')
        assert response.status_code == 200, (
            'Check that on GET request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/` '
            'without authorization token returns status 200'
        )
        data = response.json()
        assert data.get('text') == 'rewq', (
            'Check that on PATCH request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/` '
            'change the value of `text`.'
        )

        client_user = auth_client(user)
        data = {'text': 'fgf'}
        response = client_user.patch(f'{pre_url}{comments[2]["id"]}/', data=data)
        assert response.status_code == 403, (
            'Check that on PATCH request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/` '
            'from a regular user, when trying to change a review that is not their own, a status 403 is returned'
        )

        data = {'text': 'jdfk'}
        response = client_user.patch(f'{pre_url}{comments[1]["id"]}/', data=data)
        assert response.status_code == 200, (
            'Check that on PATCH request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/` '
            'returning status 200'
        )
        data = response.json()
        assert data.get('text') == 'jdfk', (
            'Check that on PATCH request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/` '
            'return object data. The value of `text` has been changed.'
        )

        client_moderator = auth_client(moderator)
        response = client_moderator.delete(f'{pre_url}{comments[1]["id"]}/')
        assert response.status_code == 204, (
            'Check that on DELETE request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/` '
            'return status 204'
        )
        response = admin_client.get(f'{pre_url}')
        test_data = response.json()['results']
        assert len(test_data) == len(comments) - 1, (
            'Check that on DELETE request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/` '
            'remove object'
        )

    def check_permissions(self, user, user_name, pre_url):
        client_user = auth_client(user)
        data = {'text': 'jdfk'}
        response = client_user.patch(pre_url, data=data)
        assert response.status_code == 403, (
            f'Check that on PATCH request `/api/v1/titles/{{title_id}}/reviews/{{review_id}}/` '
            f'with auth token {user_name} returns status 403'
        )
        response = client_user.delete(pre_url)
        assert response.status_code == 403, (
            f'Check that on DELETE request `/api/v1/titles/{{title_id}}/reviews/{{review_id}}/` '
            f'with auth token {user_name} returns status 403'
        )

    @pytest.mark.django_db(transaction=True)
    def test_04_comment_check_permission(self, client, admin_client, admin):
        comments, reviews, titles, user, moderator = create_comments(admin_client, admin)
        pre_url = f'/api/v1/titles/{titles[0]["id"]}/reviews/{reviews[0]["id"]}/comments/'
        data = {'text': 'jdfk'}
        response = client.post(f'{pre_url}', data=data)
        assert response.status_code == 401, (
            'Check that when POSTing `/api/v1/titles/{{title_id}}/reviews/{{review_id}}/comments/` '
            'no auth token returned status 401'
        )
        response = client.patch(f'{pre_url}{comments[1]["id"]}/', data=data)
        assert response.status_code == 401, (
            'Check that on PATCH request '
            '`/api/v1/titles/{{title_id}}/reviews/{{review_id}}/comments/{{comment_id}}/` '
            'no auth token returned status 401'
        )
        response = client.delete(f'{pre_url}{comments[1]["id"]}/')
        assert response.status_code == 401, (
            'Check that on DELETE request '
            '`/api/v1/titles/{{title_id}}/reviews/{{review_id}}/comments/{{comment_id}}/` '
            'no auth token returned status 401'
        )
        self.check_permissions(user, 'ordinary user', f'{pre_url}{comments[2]["id"]}/')
