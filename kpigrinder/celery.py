import os
import logging
from celery import Celery


logger = logging.getLogger('kpigrinder')


def discover_tasks():
    logger.info('Discover tasks')
    tasks_folder = os.path.join(os.path.dirname(__file__), 'tasks')
    for fl_name in os.listdir(tasks_folder):
        if fl_name.endswith('.py') and fl_name != '__init__.py':
            logger.debug('found task module: {}'.format(fl_name[:-3]))
            __import__('kpigrinder.tasks.{}'.format(fl_name[:-3]))


app = Celery('KPIgrinder')
app.config_from_object('kpigrinder.config', namespace='CELERY')
discover_tasks()
