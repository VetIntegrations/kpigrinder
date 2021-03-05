from datetime import date
from sqlalchemy.orm import session

from ghostdb.db.models.corporation import Corporation
from ghostdb.db.models.provider import Provider
from ghostdb.db.models.kpi import InternalKPIValue, KPIKind, KPIDataSource
from kpigrinder.common.kpi_calc import BaseKPICalculation


class EbitdaERP(BaseKPICalculation):

    def calculate(self, db: session.Session, dt: date):
        for provider in db.query(Provider):
            yield InternalKPIValue(
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


class Ebitda(BaseKPICalculation):

    def get_corporations(self, db: session.Session):
        return {
            name.lower(): id.hex
            for name, id in db.query(Corporation).values(Corporation.name, Corporation.id)
        }

    def calculate(self, db: session.Session, dt: date):
        bq_client = self.get_bigquery_client()

        query = bq_client.query(
            '''
            SELECT
                businesses.customer_name,
                deals.source_id,
                businesses.source_id,
                businesses.name,
                deals.ebitda,
                businesses.country,
                businesses.city,
                businesses.state,
                max(deals.updated_at)
            FROM `{dataset}.deals` as deals
            JOIN `{dataset}.businesses` as businesses on deals.source_business_id = businesses.source_id
            WHERE
                deals.ebitda is not null
                AND deals.updated_at <= '{date}'
            GROUP BY
                businesses.customer_name,
                deals.source_id,
                businesses.source_id,
                businesses.name,
                deals.ebitda,
                businesses.country,
                businesses.city,
                businesses.state
            '''.format(dataset='testing', date=dt.isoformat())
        )
        result = query.result()
        corporations = self.get_corporations(db)
        for row in result:
            yield {
                'data_source': KPIDataSource.ERP.value,
                'kind': KPIKind.FINANCIAL_EBITDA.value,
                'value': row['ebitda'],
                'date': dt.isoformat(),
                'corporation': row['customer_name'],
                'corporation_id': corporations[row['customer_name'].lower()],
                'business': row['name'],
                'business_id': row['source_id'],
                'country': row['country'],
                'city': row['city'],
                'state': row['state'],
            }
