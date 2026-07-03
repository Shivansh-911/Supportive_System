import os
import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DJANGO_ENV = os.environ.get('DJANGO_ENV', 'development')

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
    SECURE_HSTS_SECONDS=(int, 0),
    SECURE_HSTS_INCLUDE_SUBDOMAINS=(bool, False),
    SECURE_SSL_REDIRECT=(bool, False),
    SESSION_COOKIE_SECURE=(bool, False),
    CSRF_COOKIE_SECURE=(bool, False),
)
environ.Env.read_env(BASE_DIR / f'.env.{DJANGO_ENV}')

# Initialize New Relic here so it instruments all entry points (runserver, gunicorn, management commands).
# wsgi.py also calls initialize() but that is never executed by manage.py runserver.
try:
    import newrelic.agent
    newrelic.agent.initialize(BASE_DIR / 'newrelic.ini', DJANGO_ENV)
    _nr = newrelic.agent.global_settings()
    _nr.license_key = os.environ.get('NEW_RELIC_LICENSE_KEY') or _nr.license_key
    _nr.app_name = os.environ.get('NEW_RELIC_APP_NAME') or _nr.app_name
except ModuleNotFoundError:
    pass

SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env('ALLOWED_HOSTS')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'rest_framework',
    'corsheaders',
    'core.apps.CoreConfig',
    'process_agent.apps.ProcessAgentConfig',
    'question_agent.apps.QuestionAgentConfig',
    'orchestrator_agent.apps.OrchestratorAgentConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

DATABASES = {
    'default': env.db('DATABASE_URL'),
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'UTC'
USE_I18N      = True
USE_TZ        = True

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
    'DEFAULT_PARSER_CLASSES':   ['rest_framework.parsers.JSONParser'],
}

try:
    import newrelic.agent  # noqa: F401
    _NEWRELIC_AVAILABLE = True
except ModuleNotFoundError:
    _NEWRELIC_AVAILABLE = False

_logging_formatters = {
    'standard': {
        'format': '[{asctime}] [{levelname}] [{name}] {message}',
        'style': '{',
        'datefmt': '%Y-%m-%d %H:%M:%S',
    },
}
_logging_handlers = {
    'file': {
        'class': 'logging.FileHandler',
        'filename': BASE_DIR / 'logs.txt',
        'mode': 'a',
        'encoding': 'utf-8',
        'formatter': 'standard',
    },
}
_root_handlers = ['file']

if _NEWRELIC_AVAILABLE:
    _logging_formatters['newrelic'] = {'()': 'newrelic.agent.NewRelicContextFormatter'}
    _logging_handlers['newrelic'] = {'class': 'logging.StreamHandler', 'formatter': 'newrelic'}
    _root_handlers.append('newrelic')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': _logging_formatters,
    'handlers': _logging_handlers,
    'root': {
        'handlers': _root_handlers,
        'level': 'INFO',
    },
    'loggers': {
        'core':               {'level': 'DEBUG', 'propagate': True},
        'process_agent':      {'level': 'DEBUG', 'propagate': True},
        'question_agent':     {'level': 'DEBUG', 'propagate': True},
        'orchestrator_agent': {'level': 'DEBUG', 'propagate': True},
    },
}

SECURE_HSTS_SECONDS = env('SECURE_HSTS_SECONDS')
SECURE_HSTS_INCLUDE_SUBDOMAINS = env('SECURE_HSTS_INCLUDE_SUBDOMAINS')
SECURE_SSL_REDIRECT = env('SECURE_SSL_REDIRECT')
SESSION_COOKIE_SECURE = env('SESSION_COOKIE_SECURE')
CSRF_COOKIE_SECURE = env('CSRF_COOKIE_SECURE')
