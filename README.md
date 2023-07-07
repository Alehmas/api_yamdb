#  YaMDb

## Input data
This joint project was written on the basis of the terms of reference with two other developers.
I was responsible for the genres, categories and titles.

## Description
The YaMDb project collects user feedback on works. The works themselves are not stored in YaMDb,
You can't watch a movie or listen to music here.
The works are divided into categories, and a genre can also be assigned from the list of preset ones.
Only the administrator can add works, categories and genres.
Grateful or indignant users leave text reviews for the works and put
product score in the range from one to ten (integer); from user ratings
an average assessment of the work is formed - rating. For one work, the user can
leave only one review.

## Technologies used
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) ![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white) ![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray) ![JWT](https://img.shields.io/badge/JWT-black?style=for-the-badge&logo=JSON%20web%20tokens) ![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)

## YaMDb API resources
- Resource **auth**: authentication.
- Resource **users**: users.
- Resource **titles**: works to which they write reviews (a certain movie, book or song).
- Resource **categories**: categories (types) of works ("Films", "Books", "Music").
- Resource **genres**: genres of works. One work can be tied to several genres.
- Resource **reviews**: reviews of works. The review is tied to a specific product.
- Resource **comments**: comments on reviews. The comment is tied to a specific review.

## User roles and permissions
- **Anonymous** - can view descriptions of works, read reviews and comments.
- **Authenticated user** (user) - can read everything, like Anonymous, can post reviews
  and rate works, can comment on reviews; can edit
  and delete your reviews and comments, edit your ratings of works. This role is assigned
  by default for every new user.
- **Moderator** (moderator) - the same rights as the Authenticated user,
  plus the right to remove and edit any reviews and comments.
- **Administrator** (admin) — full rights to manage all project content.
  Can create and delete works, categories and genres. Can assign roles to users.
- **Django Superuser** has administrator rights, a user with admin rights.

## Run the project locally
- Clone the repository
```
git clone git@github.com:Alehmas/api_yamdb.git
```
- Move to a new directory
```
cd api_yamdb
```
- Initialize the virtual environment
```
python -m venv venv
```
- Activate the virtual environment
```
source venv/Scripts/activate
```
- Update pip and set project dependencies
```
python -m pip install --upgrade pip
pip install -r requirements.txt
```
- From the directory with the file `manage.py` run the migrations
```
python manage.py migrate
```
- Create a superuser
```
python manage.py createsuperuser
```
- To disable debug mode, change `yatube.settings.py' to
```
DEBUG = False
```
- Project launch
```
python manage.py runserver
```
- Fill out the database

## Programs for sending requests

* API testing via httpie - API console client.
If you like this console API client, [you can find installation instructions there, on the developers' website.](https://httpie.io/docs/cli/installation)

* API Testing with VS Code Extension
The extension [REST Client](https://marketplace.visualstudio.com/items?itemName=humao.rest-client) allows you to send HTTP requests directly from VS Code and view responses to them in the same interface.

* API Testing with Postman
Postman is a popular and convenient API client that can send requests and show responses, save request history and authentication data, and allow you to design and test API.
[Download Postman from the download page](https://www.postman.com/downloads/) project and install it on your work machine.

## Document examples:

`api/v1/categories/` (GET, POST, DELETE): get, create or delete a categories
```
[
  {
    "count": 0,
    "next": "string",
    "previous": "string",
    "results": [
      {
        "name": "string",
        "slug": "string"
      }
    ]
  }
]
```
`api/v1/genres/` (GET, POST, DELETE): get, create or delete a genres
```
[
  {
  "count": 0,
  "next": "string",
  "previous": "string",
  "results": [
    {
      "name": "string",
      "slug": "string"
    }
  ]
  }
]
```
`api/v1/titles/` (GET, POST, PUTCH, DELETE): get, create, update or delete a titles
```
[
  {
    "count": 0,
    "next": "string",
    "previous": "string",
    "results": [
      {
        "id": 0,
        "name": "string",
        "year": 0,
        "rating": 0,
        "description": "string",
        "genre": [
            {
              "name": "string",
              "slug": "string"
            }
          ],
        "category": {
          "name": "string",
          "slug": "string"
        }
      }
    ]
  }
]
```

## Request examples
Examples of requests, access rights, possible answers are available in the [documentation](http://127.0.0.1:8000/redoc/) attached to the project 

## Authors
- [Aleh Maslau](https://github.com/Alehmas)
