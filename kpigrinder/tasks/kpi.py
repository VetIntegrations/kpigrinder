from datetime import date
from celery import shared_task

from kpigrinder import config
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
    # KPIValue instance as we operate only IDs but for some storages need to have
    # names as well
    kpi_calc = KPICalcClass([gdb_stor, bq_stor])
    kpi_calc.process(dt)
