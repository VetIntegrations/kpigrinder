from datetime import date
from celery import shared_task

from kpigrinder.utils.module_loading import import_string


@shared_task
def kpi_calculate(kpi_class_path: str, dt: date):
    KPICalcClass = import_string(kpi_class_path)

    kpi_calc = KPICalcClass([])
    kpi_calc.process(dt)
