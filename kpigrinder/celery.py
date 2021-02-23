import os
import logging
import sentry_sdk
from celery import Celery, Task
from sentry_sdk.integrations.celery import CeleryIntegration

from ghostdb.db import meta
from kpigrinder import config
from kpigrinder.utils.db import DBAppTaskMixin


logger = logging.getLogger('kpigrinder')


class CeleryBaseTask(DBAppTaskMixin, Task):
    pass


def discover_tasks():
    logger.info('Discover tasks')
    tasks_folder = os.path.join(os.path.dirname(__file__), 'tasks')
    for fl_name in os.listdir(tasks_folder):
        if fl_name.endswith('.py') and fl_name != '__init__.py':
            logger.debug('found task module: {}'.format(fl_name[:-3]))
            __import__('kpigrinder.tasks.{}'.format(fl_name[:-3]))


app = Celery('KPIgrinder', task_cls=CeleryBaseTask)
app.config_from_object('kpigrinder.config', namespace='CELERY')
if config.SENTRY_DSN:
    sentry_sdk.init(
        dsn=config.SENTRY_DSN,
        integrations=[CeleryIntegration()]
    )

discover_tasks()

meta.initialize()
