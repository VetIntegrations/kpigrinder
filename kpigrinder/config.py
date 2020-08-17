from envparse import env


env.read_envfile('environment')

GCP_PROJECT_ID = env.str('GCP_PROJECT_ID')

CELERY_BROKER_URL = env.str('CELERY_BROKER_URL')
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_ACCEPT_CONTENT = ('application/x-python-serialize', )

SECRET_MANAGER_NAME_PREFIX = env.str('SECRET_MANAGER_NAME_PREFIX', default='')
