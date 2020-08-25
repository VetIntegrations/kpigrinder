from envparse import env
from celery.schedules import crontab


env.read_envfile('environment')

GCP_PROJECT_ID = env.str('GCP_PROJECT_ID')

CELERY_BROKER_URL = env.str('CELERY_BROKER_URL')
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_ACCEPT_CONTENT = ('application/x-python-serialize', )
CELERY_BEAT_SCHEDULE = {
    'daily_kpi_calculations': {
        'task': 'kpigrinder.tasks.kpi.run_all_kpi_calculation',
        'schedule': crontab(minute=10, hour=0),
    },
}

SENTRY_DSN = env.str('SENTRY_DSN')

SECRET_MANAGER_NAME_PREFIX = env.str('SECRET_MANAGER_NAME_PREFIX', default='')

STORAGE_REGISTRY_TTL = 60 * 10  # 10 minues

BIGQUERY_KPI_TABLE_NAME = env.str('BIGQUERY_KPI_TABLE_NAME')

CONNECTION_GHOSTDB = env.str('CONNECTION_GHOSTDB', default='credentials-connection-ghostdb')
