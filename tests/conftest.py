import os
import sys

from django.utils.version import get_version

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
root_dir_content = os.listdir(BASE_DIR)
PROJECT_DIR_NAME = 'api_yamdb'
if (
        PROJECT_DIR_NAME not in root_dir_content
        or not os.path.isdir(os.path.join(BASE_DIR, PROJECT_DIR_NAME))
):
    assert False, (
        f'The folder with the project `{PROJECT_DIR_NAME}` was not found in the directory `{BASE_DIR}`. '
        f'Make sure you have the correct project structure.'
    )

MANAGE_PATH = os.path.join(BASE_DIR, PROJECT_DIR_NAME)
project_dir_content = os.listdir(MANAGE_PATH)
FILENAME = 'manage.py'
if FILENAME not in project_dir_content:
    assert False, (
        f'File `{FILENAME}` was not found in directory `{MANAGE_PATH}`. '
        f'Make sure you have the correct project structure.'
    )

assert get_version() < '3.0.0', 'Please use Django version < 3.0.0'

pytest_plugins = [
    'tests.fixtures.fixture_user',
]
