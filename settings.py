"""
Django settings for finan project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys
import platform
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '=l-1$wwm*(zgj6c$dwp(tvcw_7n(v!3*37w_ng@9avilj#an#j'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = True

#ALLOWED_HOSTS = ['*']
ALLOWED_HOSTS = ['secure-mountain-6385.herokuapp.com']

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'finance',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'urls'

WSGI_APPLICATION = 'wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         #'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#         'NAME': 'balance.db',
#     }
# }

# DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
#             'NAME': 'balance',                      # Or path to database file if using sqlite3.
#             # The following settings are not used with sqlite3:
#             'USER': 'balance',
#             'PASSWORD': 'dengo',
#             'HOST': 'localhost',                      # Empty for localhost through domain sockets or           '127.0.0.1' for localhost through TCP.
#             'PORT': '5432',                      # Set to empty string for default.
#         }
#     }

# Parse database configuration from $DATABASE_URL
import dj_database_url

DATABASES = { 'default' : dj_database_url.config()}
# we only need the engine name, as heroku takes care of the rest
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
    }
}

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# try to load local_settings.py if it exists
# try:
#   from local_settings import *
# except Exception as e:
#   pass

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

EMAIL_GOOGLE = ''
SENHA_GOOGLE = ''
DOC_KEY_GOOGLE = ''

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

try:
	local = open(os.path.join(sys.path[0],'settings_local.py')).read()
	exec(local)
except IOError:
	pass