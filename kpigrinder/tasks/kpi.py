from datetime import date, timedelta
from celery import shared_task

from kpigrinder import config
from kpigrinder.calculators.registry import KPIRegistry
from kpigrinder.common.storage.registry import StorageRegistry
from kpigrinder.common.storage.bigquery import BigQueryStorage
from kpigrinder.common.storage.ghostdb import GhostDBStorage
from kpigrinder.utils.module_loading import import_string
from kpigrinder.utils.secret_manager import SecretManager


@shared_task
def kpi_calculate(kpi_class_path: str, dt: date):
    sm = SecretManager()
    KPICalcClass = import_string(kpi_class_path)

    stor_registry = StorageRegistry()
    gdb_stor = stor_registry.get_storage(GhostDBStorage, sm.get_secret(config.CONNECTION_GHOSTDB))
    bq_stor = stor_registry.get_storage(BigQueryStorage, {'table_name': config.BIGQUERY_KPI_TABLE_NAME})

    # GhostDB Storage should be first in the list to prefill all related objects in
    # InternalKPIValue instance as we operate only IDs but for some storages need to have
    # names as well
    kpi_calc = KPICalcClass([gdb_stor, bq_stor])
    kpi_calc.process(dt)


@shared_task
def run_all_kpi_calculation(date_start=None, date_end=None):
    if date_start is None:
        date_start = date.today() - timedelta(days=1)

    if date_end is None:
        date_end = date.today()
    elif date_end <= date_start:
        raise TaskParamException('date_end should be greater then date_start')

    dt = date_start
    while dt < date_end:
        for kpi_class_path in KPIRegistry.get_classes_path():
            kpi_calculate.delay(
                kpi_class_path=kpi_class_path,
                dt=dt
            )

        dt += timedelta(days=1)


class TaskParamException(Exception):
    ...
