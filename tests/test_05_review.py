import pytest

from .common import (auth_client, create_reviews, create_titles,
                     create_users_api)


class Test05ReviewAPI:

    @pytest.mark.django_db(transaction=True)
    def test_01_review_not_auth(self, client, admin_client):
        titles, _, _ = create_titles(admin_client)
        response = client.get(f'/api/v1/titles/{titles[0]["id"]}/reviews/')
        assert response.status_code != 404, (
            'Page `/api/v1/titles/{title_id}/reviews/` not found, check this address in *urls.py*'
        )
        assert response.status_code == 200, (
            'Check that on GET request `/api/v1/titles/{title_id}/reviews/` '
            'without authorization token returns status 200'
        )

    def create_review(self, client_user, title_id, text, score):
        data = {'text': text, 'score': score}
        response = client_user.post(f'/api/v1/titles/{title_id}/reviews/', data=data)
        assert response.status_code == 201, (
            'Check that when POSTing `/api/v1/titles/{title_id}/reviews/` '
            'with correct data returns status 201, api is available to any authenticated user'
        )
        return response

    @pytest.mark.django_db(transaction=True)
    def test_02_review_admin(self, admin_client, admin):
        titles, _, _ = create_titles(admin_client)
        user, moderator = create_users_api(admin_client)
        client_user = auth_client(user)
        client_moderator = auth_client(moderator)
        data = {}
        response = admin_client.post(f'/api/v1/titles/{titles[0]["id"]}/reviews/', data=data)
        assert response.status_code == 400, (
            'Check that when POSTing `/api/v1/titles/{title_id}/reviews/` '
            'with invalid data returns status 400'
        )
        self.create_review(admin_client, titles[0]["id"], 'qwerty', 5)
        data = {
            'text': 'Hat',
            'score': 1
        }
        response = admin_client.post(f'/api/v1/titles/{titles[0]["id"]}/reviews/', data=data)
        code = 400
        assert response.status_code == code, (
            'Check that when POSTing a request to `/api/v1/titles/{title_id}/reviews/` '
            'cannot add a second review to the same work, and returns '
            f'status {code}'
        )
        try:
            from reviews.models import Review, Title
        except Exception as e:
            assert False, (
                'Failed to import models from the reviews application. '
                f'Error: {e}'
            )
        from django.db.utils import IntegrityError
        title = Title.objects.get(pk=titles[0]["id"])
        review = None
        try:
            review = Review.objects.create(
                text='Second review text',
                score='5',
                author=admin,
                title=title
            )
        except IntegrityError:
            pass

        assert review is None, (
            'Check that via a direct request to Django ORM '
            'You cannot add a second review to the same work. '
            'This check is done at the model level.'
        )
        response = admin_client.put(f'/api/v1/titles/{titles[0]["id"]}/reviews/', data=data)
        code = 405
        assert response.status_code == code, (
            'Check that PUT request to `/api/v1/titles/{title_id}/reviews/` '
            'not allowed and returned '
            f'status {code}'
        )
        self.create_review(client_user, titles[0]["id"], 'Well, that', 3)
        self.create_review(client_moderator, titles[0]["id"], 'Will go for a beer', 4)

        self.create_review(admin_client, titles[1]["id"], 'More about nothing', 2)
        self.create_review(client_user, titles[1]["id"], 'Normal', 4)
        response = self.create_review(client_moderator, titles[1]["id"], 'So-so', 3)

        assert type(response.json().get('id')) == int, (
            'Check that when POSTing `/api/v1/titles/{title_id}/reviews/` '
            'return the data of the created object. The value of `id` is not present or is not an integer.'
        )

        data = {'text': 'kjdfg', 'score': 4}
        response = admin_client.post('/api/v1/titles/999/reviews/', data=data)
        assert response.status_code == 404, (
            'Check that when POSTing `/api/v1/titles/{title_id}/reviews/` '
            'with a non-existent title_id, a 404 status is returned.'
        )
        data = {'text': 'asfd', 'score': 11}
        response = admin_client.post(f'/api/v1/titles/{titles[0]["id"]}/reviews/', data=data)
        assert response.status_code == 400, (
            'Check that when POSTing `/api/v1/titles/{title_id}/reviews/` '
            'with `score` greater than 10, status 400 is returned.'
        )
        data = {'text': 'asfd', 'score': 0}
        response = admin_client.post(f'/api/v1/titles/{titles[0]["id"]}/reviews/', data=data)
        assert response.status_code == 400, (
            'Probably when POSTing `/api/v1/titles/{title_id}/reviews/` '
            'with `score` less than 1 returns status 400.'
        )
        data = {'text': 'asfd', 'score': 2}
        response = admin_client.post(f'/api/v1/titles/{titles[0]["id"]}/reviews/', data=data)
        assert response.status_code == 400, (
            'Check that when POSTing `/api/v1/titles/{title_id}/reviews/` '
            'A status 400 is returned for an object that has already been reviewed.'
        )

        response = admin_client.get(f'/api/v1/titles/{titles[0]["id"]}/reviews/')
        assert response.status_code == 200, (
            'Check that GET request `/api/v1/titles/{title_id}/reviews/` returns status 200'
        )
        data = response.json()
        assert 'count' in data, (
            'Check that a GET request to `/api/v1/titles/{title_id}/reviews/` returns data with pagination. '
            'Parameter `count` not found'
        )
        assert 'next' in data, (
            'Check that a GET request to `/api/v1/titles/{title_id}/reviews/` returns data with pagination. '
            'Parameter `next` not found'
        )
        assert 'previous' in data, (
            'Check that a GET request to `/api/v1/titles/{title_id}/reviews/` returns data with pagination. '
            'Parameter `previous` not found'
        )
        assert 'results' in data, (
            'Check that a GET request to `/api/v1/titles/{title_id}/reviews/` returns data with pagination. '
            'Parameter `results` not found'
        )
        assert data['count'] == 3, (
            'Check that a GET request to `/api/v1/titles/{title_id}/reviews/` returns data with pagination. '
            'The value of the `count` parameter is invalid'
        )
        assert type(data['results']) == list, (
            'Check that a GET request to `/api/v1/titles/{title_id}/reviews/` returns data with pagination. '
            'The type of the `results` parameter must be a list'
        )
        assert len(data['results']) == 3, (
            'Check that a GET request to `/api/v1/titles/{title_id}/reviews/` returns data with pagination. '
            'The value of the `results` parameter is invalid'
        )

        if data['results'][0].get('text') == 'qwerty':
            review = data['results'][0]
        elif data['results'][1].get('text') == 'qwerty':
            review = data['results'][1]
        elif data['results'][2].get('text') == 'qwerty':
            review = data['results'][2]
        else:
            assert False, (
                'Check that on GET request `/api/v1/titles/{title_id}/reviews/` '
                'return data with pagination. The value of the `results` parameter is invalid, '
                '`text` not found or not saved on POST request.'
            )

        assert review.get('score') == 5, (
            'Check that a GET request to `/api/v1/titles/{title_id}/reviews/` returns data with pagination. '
            'The value of the `results` parameter is invalid, `score` was not found or was not saved in the POST request'
        )
        assert review.get('author') == admin.username, (
            'Check that a GET request to `/api/v1/titles/{title_id}/reviews/` returns data with pagination. '
            'The value of the `results` parameter is invalid, `author` was not found or was not saved in the POST request.'
        )
        assert review.get('pub_date'), (
            'Check that a GET request to `/api/v1/titles/{title_id}/reviews/` returns data with pagination. '
            'The value of the `results` parameter is invalid, `pub_date` not found.'
        )
        assert type(review.get('id')) == int, (
            'Check that a GET request to `/api/v1/titles/{title_id}/reviews/` returns data with pagination. '
            'The value of the `results` parameter is invalid, the value of `id` is not present or is not an integer.'
        )

        response = admin_client.get(f'/api/v1/titles/{titles[0]["id"]}/')
        data = response.json()
        assert data.get('rating') == 4, (
            'Check that GET request `/api/v1/titles/{title_id}/` '
            'with reviews returns the correct value of `rating`'
        )
        response = admin_client.get(f'/api/v1/titles/{titles[1]["id"]}/')
        data = response.json()
        assert data.get('rating') == 3, (
            'Check that GET request `/api/v1/titles/{title_id}/` '
            'with reviews returns the correct value of `rating`'
        )

    @pytest.mark.django_db(transaction=True)
    def test_03_review_detail(self, client, admin_client, admin):
        reviews, titles, user, moderator = create_reviews(admin_client, admin)
        response = client.get(f'/api/v1/titles/{titles[0]["id"]}/reviews/{reviews[0]["id"]}/')
        assert response.status_code != 404, (
            'Page `/api/v1/titles/{title_id}/reviews/{review_id}/` not found, check this address in *urls.py*'
        )
        assert response.status_code == 200, (
            'Check that on GET request `/api/v1/titles/{title_id}/reviews/{review_id}/` '
            'without authorization token returns status 200'
        )
        data = response.json()
        assert type(data.get('id')) == int, (
            'Check that on GET request `/api/v1/titles/{title_id}/reviews/{review_id}/` '
            'return object data. The value of `id` is not present or is not an integer.'
        )
        assert data.get('score') == reviews[0]['score'], (
            'Check that on GET request `/api/v1/titles/{title_id}/reviews/{review_id}/` '
            'return object data. The value of `score` is invalid.'
        )
        assert data.get('text') == reviews[0]['text'], (
            'Check that on GET request `/api/v1/titles/{title_id}/reviews/{review_id}/` '
            'return object data. The value of `text` is invalid.'
        )
        assert data.get('author') == reviews[0]['author'], (
            'Check that on GET request `/api/v1/titles/{title_id}/reviews/{review_id}/` '
            'return object data. The value of `author` is invalid.'
        )

        review_text = 'Top finally!!'
        data = {
            'text': review_text,
            'score': 10
        }
        response = admin_client.patch(f'/api/v1/titles/{titles[0]["id"]}/reviews/{reviews[0]["id"]}/', data=data)
        assert response.status_code == 200, (
            'Check that on PATCH request `/api/v1/titles/{title_id}/reviews/{review_id}/` '
            'returning status 200'
        )
        data = response.json()
        assert data.get('text') == review_text, (
            'Check that on PATCH request `/api/v1/titles/{title_id}/reviews/{review_id}/` '
            'return object data. The value of `text` has been changed.'
        )
        response = admin_client.get(f'/api/v1/titles/{titles[0]["id"]}/reviews/{reviews[0]["id"]}/')
        assert response.status_code == 200, (
            'Check that on GET request `/api/v1/titles/{title_id}/reviews/{review_id}/` '
            'without authorization token returns status 200'
        )
        data = response.json()
        assert data.get('text') == review_text, (
            'Check that on PATCH request `/api/v1/titles/{title_id}/reviews/{review_id}/` '
            'change the value of `text`.'
        )
        assert data.get('score') == 10, (
            'Check that on PATCH request `/api/v1/titles/{title_id}/reviews/{review_id}/` '
            'change the value of `score`.'
        )

        client_user = auth_client(user)
        data = {
            'text': 'fgf',
            'score': 1
        }
        response = client_user.patch(f'/api/v1/titles/{titles[0]["id"]}/reviews/{reviews[2]["id"]}/', data=data)
        assert response.status_code == 403, (
            'Check that on PATCH request `/api/v1/titles/{title_id}/reviews/{review_id}/` '
            'from a regular user, when trying to change a review that is not their own, a status 403 is returned'
        )

        data = {
            'text': 'jdfk',
            'score': 7
        }
        response = client_user.patch(f'/api/v1/titles/{titles[0]["id"]}/reviews/{reviews[1]["id"]}/', data=data)
        assert response.status_code == 200, (
            'Check that on PATCH request `/api/v1/titles/{title_id}/reviews/{review_id}/` '
            'returning status 200'
        )
        data = response.json()
        assert data.get('text') == 'jdfk', (
            'Check that on PATCH request `/api/v1/titles/{title_id}/reviews/{review_id}/` '
            'return object data. The value of `text` has been changed.'
        )
        response = admin_client.get(f'/api/v1/titles/{titles[0]["id"]}/')
        data = response.json()
        assert data.get('rating') == 7, (
            'Check that GET request `/api/v1/titles/{title_id}/` '
            'with reviews returns the correct value of `rating`'
        )

        client_moderator = auth_client(moderator)
        response = client_moderator.delete(f'/api/v1/titles/{titles[0]["id"]}/reviews/{reviews[1]["id"]}/')
        assert response.status_code == 204, (
            'Check that on DELETE request `/api/v1/titles/{title_id}/reviews/{review_id}/` '
            'return status 204'
        )
        response = admin_client.get(f'/api/v1/titles/{titles[0]["id"]}/reviews/')
        test_data = response.json()['results']
        assert len(test_data) == len(reviews) - 1, (
            'Check that when you DELETE request `/api/v1/titles/{title_id}/reviews/{review_id}/` you are deleting the object'
        )

    def check_permissions(self, user, user_name, reviews, titles):
        client_user = auth_client(user)
        data = {'text': 'jdfk', 'score': 7}
        response = client_user.patch(f'/api/v1/titles/{titles[0]["id"]}/reviews/{reviews[0]["id"]}/', data=data)
        assert response.status_code == 403, (
            f'Check that on PATCH request `/api/v1/titles/{{title_id}}/reviews/{{review_id}}/` '
            f'with auth token {user_name} returns status 403'
        )
        response = client_user.delete(f'/api/v1/titles/{titles[0]["id"]}/reviews/{reviews[0]["id"]}/')
        assert response.status_code == 403, (
            f'Check that on DELETE request `/api/v1/titles/{{title_id}}/reviews/{{review_id}}/` '
            f'with auth token {user_name} returns status 403'
        )

    @pytest.mark.django_db(transaction=True)
    def test_04_reviews_check_permission(self, client, admin_client, admin):
        reviews, titles, user, moderator = create_reviews(admin_client, admin)
        data = {'text': 'jdfk', 'score': 7}
        response = client.post(f'/api/v1/titles/{titles[0]["id"]}/reviews/', data=data)
        assert response.status_code == 401, (
            'Check that when POSTing `/api/v1/titles/{{title_id}}/reviews/` '
            'no auth token returned status 401'
        )
        response = client.patch(f'/api/v1/titles/{titles[0]["id"]}/reviews/{reviews[1]["id"]}/', data=data)
        assert response.status_code == 401, (
            'Check that on PATCH request `/api/v1/titles/{{title_id}}/reviews/{{review_id}}/` '
            'no auth token returned status 401'
        )
        response = client.delete(f'/api/v1/titles/{titles[0]["id"]}/reviews/{reviews[1]["id"]}/')
        assert response.status_code == 401, (
            'Check that on DELETE request `/api/v1/titles/{{title_id}}/reviews/{{review_id}}/` '
            'no auth token returned status 401'
        )
        self.check_permissions(user, 'ordinary user', reviews, titles)
