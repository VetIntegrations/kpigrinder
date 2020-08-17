from datetime import date
from sqlalchemy.orm import session

from ghostdb.db.models.provider import Provider
from ghostdb.db.models.kpi import KPIValue, KPIKind, KPIDataSource
from kpigrinder.common.kpi_calc import BaseKPICalculation


class EbitdaERP(BaseKPICalculation):

    def calculate(self, db: session.Session, dt: date):
        for provider in db.query(Provider):
            yield KPIValue(
                data_source=KPIDataSource.ERP,
                kind=KPIKind.FINANCIAL_EBITDA,
                value=0,
                date=dt,
                corporation_id=provider.business.corporation_id,
                business_id=provider.business_id,
                provider_id=provider.id,
                # revenue_center_id=transaction.revenue_center_id,
                # department_id=transaction.department_id,
                # class_id=transaction.class_id
            )
