from envparse import env


env.read_envfile('environment')

CELERY_BROKER_URL = 'redis://localhost:6379/5'
