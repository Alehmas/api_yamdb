import os

from .conftest import MANAGE_PATH, project_dir_content, root_dir_content


api_path = os.path.join(MANAGE_PATH, 'api')
if 'api' in project_dir_content and os.path.isdir(api_path):
    api_dir_content = os.listdir(api_path)
    assert 'models.py' not in api_dir_content, (
        f'The `{api_path}` directory must not contain a model file. '
        'They are not needed in this application.'
    )
else:
    assert False, f'Application `api` not found in folder {MANAGE_PATH}'


# test .md
default_md = '# api_yamdb\napi_yamdb\n'
filename = 'README.md'
assert filename in root_dir_content, (
    f'File `{filename}` not found in project root'
)

with open(filename, 'r') as f:
    file = f.read()
    assert file != default_md, (
        f'Don`t forget to style `{filename}`'
    )
