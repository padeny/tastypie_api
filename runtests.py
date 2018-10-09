import sys
import os

from django.conf import settings
from django.core.management import execute_from_command_line

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


if not settings.configured:
    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
            }
        },
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.sessions',
            'django.contrib.contenttypes',
            'mas_tastypie_api',
            'test',
        ],
        ROOT_URLCONF="test.urls",
        MIDDLEWARE_CLASSES=[
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
        ],
        TEMPLATES=[
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'APP_DIRS': True,
                'OPTIONS': {
                    'context_processors': [
                        'django.template.context_processors.request',
                        'django.contrib.auth.context_processors.auth',
                    ],
                },
            },
        ],
        ALLOWED_HOSTS=['*'],

    )


def runtests():
    # import pdb; pdb.set_trace()
    # argv = sys.argv[:1] + ['runserver'] + sys.argv[1:]
    if len(sys.argv) == 1:
        argv = sys.argv[:1] + ['test']
    else:
        argv = sys.argv
    execute_from_command_line(argv)


if __name__ == '__main__':
    runtests()
