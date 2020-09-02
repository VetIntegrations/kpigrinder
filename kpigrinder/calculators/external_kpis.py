from datetime import date
from sqlalchemy.orm import session

from ghostdb.db.models.business import Business
from ghostdb.bl.selectors.kpi import ExternalKPIValueSelector
from kpigrinder.common.kpi_calc import BaseKPICalculation


class GenericExternalKPICalculation(BaseKPICalculation):

    def calculate(self, db: session.Session, dt: date):
        kpi_selector = ExternalKPIValueSelector(db)

        businesses = db.query(Business)
        for business in businesses:
            query, ok = kpi_selector.by_business(business.id)
            kpi_value_query = kpi_selector.filter_by_timerange(query, dt)
            for kpi_value in kpi_value_query:
                yield kpi_value
