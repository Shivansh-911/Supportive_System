import os

try:
    import newrelic.agent
    newrelic.agent.initialize(
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'newrelic.ini'),
        os.environ.get('DJANGO_ENV', 'development'),
    )
except ModuleNotFoundError:
    pass

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_wsgi_application()
