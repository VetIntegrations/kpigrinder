from datetime import date, datetime, timedelta
from itertools import groupby
from sqlalchemy import func
from sqlalchemy.orm import session
from sqlalchemy.orm.util import aliased

from ghostdb.bl.selectors.kpi import KPISelector
from ghostdb.db.models.business import Business
from ghostdb.db.models.order import Order, OrderItem
from ghostdb.db.models.provider import Provider
from ghostdb.db.models.kpi import KPIValue, KPIKind, KPIDataSource
from kpigrinder.common.kpi_calc import BaseKPICalculation
from kpigrinder.calculators.utils import GeneralGroupAndAggregate
from . import common as finance_common


class NetProfitPMS(BaseKPICalculation):

    def calculate(self, db: session.Session, dt: date):
        kpi_selector = KPISelector(db)

        order_rel = aliased(Order)

        dt_from = datetime.combine(dt, datetime.min.time())
        dt_to = dt_from + timedelta(days=1)

        businesses = db.query(Business)
        for business in businesses:
            gross_revenue = finance_common.get_gross_revenue(
                kpi_selector,
                business,
                dt_from,
                dt_to,
                order_rel,
                GeneralGroupAndAggregate
            )
            inventory = self.get_inventory(kpi_selector, business, dt_from, dt_to, order_rel)

            data = gross_revenue + inventory
            groupped = groupby(
                sorted(data, key=GeneralGroupAndAggregate.key_builder),
                key=GeneralGroupAndAggregate.key_builder
            )

            for _key, transactions in groupped:
                value = 0
                for transaction in transactions:
                    value += getattr(transaction, 'amount', 0) - getattr(transaction, 'inventory_amount', 0)

                if value == 0:
                    continue

                yield KPIValue(
                    data_source=KPIDataSource.PIMS,
                    kind=KPIKind.FINANCIAL_NET_PROFIT,
                    value=value,
                    date=dt,
                    corporation_id=transaction.corporation_id,
                    business_id=transaction.business_id,
                    provider_id=transaction.provider_id,
                    revenue_center_id=transaction.revenue_center_id,
                    department_id=transaction.department_id,
                    category_id=transaction.category_id,
                    class_id=transaction.class_id
                )

    @staticmethod
    def get_gross_revenue(
        kpi_selector: KPISelector,
        business: Business,
        dt_from: datetime,
        dt_to: datetime,
        order_rel
    ):
        query, ok = kpi_selector.pms_gross_revenue.orderitem_with_all_filters(
            business,
            dt_from,
            dt_to,
            order_rel=order_rel
        )

        qs = GeneralGroupAndAggregate.group_and_aggregate(
            query,
            [
                (
                    'amount',
                    func.sum(func.IF(
                        OrderItem.unit_price.is_(None),
                        OrderItem.amount / 100,
                        OrderItem.unit_price * OrderItem.quantity / 100
                    ))
                ),
            ]
        )

        return qs.all()

    @staticmethod
    def get_inventory(
        kpi_selector: KPISelector,
        business: Business,
        dt_from: datetime,
        dt_to: datetime,
        order_rel,
        query_filter: dict = None
    ):
        query, ok = kpi_selector.pms_inventory_transactions.orderitem_with_all_filters(
            business,
            dt_from,
            dt_to,
            order_rel=order_rel
        )
        if query_filter:
            query = query.filter(**query_filter)

        qs = GeneralGroupAndAggregate.group_and_aggregate(
            query,
            [
                (
                    'inventory_amount',
                    func.sum(func.IF(
                        OrderItem.unit_price.is_(None),
                        OrderItem.amount / 100,
                        OrderItem.unit_price * OrderItem.quantity / 100
                    ))
                ),
            ]
        )

        return qs.all()


class NetProfitERP(BaseKPICalculation):

    def calculate(self, db: session.Session, dt: date):
        for provider in db.query(Provider):
            yield KPIValue(
                data_source=KPIDataSource.ERP,
                kind=KPIKind.FINANCIAL_NET_PROFIT,
                value=0,
                date=dt,
                corporation_id=provider.business.corporation_id,
                business_id=provider.business_id,
                provider_id=provider.id,
                # revenue_center_id=transaction.revenue_center_id,
                # department_id=transaction.department_id,
                # class_id=transaction.class_id
            )
