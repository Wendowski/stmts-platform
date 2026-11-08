import os
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'development-only-never-deploy')
DEBUG = os.environ.get('STMTS_DEVELOPMENT', '0') == '1'
if not DEBUG and SECRET_KEY == 'development-only-never-deploy':
    raise RuntimeError('Set DJANGO_SECRET_KEY outside development')
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver']
ROOT_URLCONF = 'config.urls'
INSTALLED_APPS = ['django.contrib.contenttypes', 'rest_framework']
MIDDLEWARE = ['django.middleware.security.SecurityMiddleware', 'django.middleware.common.CommonMiddleware']
REST_FRAMEWORK = {'DEFAULT_AUTHENTICATION_CLASSES': [], 'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.AllowAny'], 'UNAUTHENTICATED_USER': None}
USE_TZ = True
DATABASES = {'default': {'ENGINE': 'django.db.backends.postgresql', 'NAME': os.environ.get('POSTGRES_DB', 'stmts'), 'USER': os.environ.get('POSTGRES_USER', 'stmts'), 'PASSWORD': os.environ.get('POSTGRES_PASSWORD', ''), 'HOST': os.environ.get('POSTGRES_HOST', 'localhost'), 'PORT': '5432'}}
