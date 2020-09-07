from datetime import date
from sqlalchemy import func
from sqlalchemy.orm import session
from sqlalchemy.sql import label

from ghostdb.bl.selectors.kpi import KPISelector
from ghostdb.db.models.business import Business
from ghostdb.db.models.provider import Provider
from ghostdb.db.models.payment import Payment
from ghostdb.db.models.kpi import InternalKPIValue, KPIKind, KPIDataSource
from kpigrinder.common.kpi_calc import BaseKPICalculation


class CogsPMS(BaseKPICalculation):

    def calculate(self, db: session.Session, dt: date):
        kpi_selector = KPISelector(db)
        businesses = db.query(Business)

        for business in businesses:
            # Until we don’t have real payment data and use “mock” table with time,
            # only pure date is using. Should be changed after we will understand real data
            dt_from, dt_to = self.get_datetime_range_with_time_zone(dt, tz=None)
            query, ok = kpi_selector.pms_cogs.payments_with_all_filters(business, dt_from, dt_to)
            query = (
                query
                .with_entities(
                    label('corporation_id', Payment.corporation_id),
                    label('business_id', Payment.business_id),
                    label('provider_id', Payment.provider_id),
                    label('amount', func.sum(Payment.value)),
                )
                .group_by(
                    Payment.corporation_id,
                    Payment.business_id,
                    Payment.provider_id,
                )
            )

            for item in query:
                yield InternalKPIValue(
                    data_source=KPIDataSource.PIMS,
                    kind=KPIKind.FINANCIAL_COGS,
                    value=item.amount,
                    date=dt,
                    corporation_id=item.corporation_id,
                    business_id=item.business_id,
                    provider_id=item.provider_id,
                )


class CogsERP(BaseKPICalculation):

    def calculate(self, db: session.Session, dt: date):
        for provider in db.query(Provider):
            yield InternalKPIValue(
                data_source=KPIDataSource.ERP,
                kind=KPIKind.FINANCIAL_COGS,
                value=0,
                date=dt,
                corporation_id=provider.business.corporation_id,
                business_id=provider.business_id,
                provider_id=provider.id,
                # revenue_center_id=transaction.revenue_center_id,
                # department_id=transaction.department_id,
                # class_id=transaction.class_id
            )
