import os
from datetime import timedelta

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'accounts',
    'posts',
    'clubs',
    'watchlist',
]

AUTH_USER_MODEL = 'accounts.User' # IMPORTANT - custom user from start

MIDDLEWARE = ['corsheaders.middleware.CorsMiddleware'] + [...]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ('rest_framework_simplejwt.authentication.JWTAuthentication',),
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticatedOrReadOnly',)
}

SIMPLE_JWT = {'ACCESS_TOKEN_LIFETIME': timedelta(days=1)}

CORS_ALLOW_ALL_ORIGINS = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME','moviedb'),
        'USER': os.getenv('DB_USER','postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD','postgres'),
        'HOST': os.getenv('DB_HOST','db'),
        'PORT': '5432',
    }
}