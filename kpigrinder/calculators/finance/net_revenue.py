from datetime import date, datetime
from itertools import groupby
from sqlalchemy import func
from sqlalchemy.orm import session
from sqlalchemy.orm.util import aliased

from ghostdb.bl.selectors.kpi import KPISelector
from ghostdb.db.models.business import Business
from ghostdb.db.models.provider import Provider
from ghostdb.db.models.order import Order, OrderItem
from ghostdb.db.models.kpi import InternalKPIValue, KPIKind, KPIDataSource
from kpigrinder.common.kpi_calc import BaseKPICalculation
from kpigrinder.calculators.utils import ClientGroupAndAggregate
from . import common as finance_common


class NetRevenuePMS(BaseKPICalculation):

    def calculate(self, db: session.Session, dt: date):
        kpi_selector = KPISelector(db)
        order_rel = aliased(Order)
        businesses = db.query(Business).all()

        for business in businesses:
            dt_from, dt_to = self.get_datetime_range_with_time_zone(dt, tz=business.timezone)
            gross_revenue = finance_common.get_gross_revenue(
                kpi_selector,
                business,
                dt_from,
                dt_to,
                order_rel,
                ClientGroupAndAggregate
            )
            discounts = self.get_discounts(kpi_selector, business, dt_from, dt_to, order_rel)
            refunds = self.get_refunds(kpi_selector, business, dt_from, dt_to, order_rel)

            data = gross_revenue + discounts + refunds
            groupped = groupby(
                sorted(data, key=ClientGroupAndAggregate.key_builder),
                key=ClientGroupAndAggregate.key_builder
            )
            for _key, transactions in groupped:
                value = 0
                for transaction in transactions:
                    value += (
                        getattr(transaction, 'amount', 0)
                        - getattr(transaction, 'discount_amount', 0)
                        - abs(getattr(transaction, 'refund_amount', 0))
                    )

                if value == 0:
                    continue

                yield InternalKPIValue(
                    data_source=KPIDataSource.PIMS,
                    kind=KPIKind.FINANCIAL_NET_REVENUE,
                    value=value,
                    date=dt,
                    corporation_id=transaction.corporation_id,
                    business_id=transaction.business_id,
                    provider_id=transaction.provider_id,
                    client_id=transaction.client_id,
                    revenue_center_id=transaction.revenue_center_id,
                    department_id=transaction.department_id,
                    category_id=transaction.category_id,
                    class_id=transaction.class_id
                )

    @staticmethod
    def get_discounts(
        kpi_selector: KPISelector,
        business: Business,
        dt_from: datetime,
        dt_to: datetime,
        order_rel
    ):
        query, ok = kpi_selector.pms_discount.orderitem_with_all_filters(
            business,
            dt_from,
            dt_to,
            order_rel=order_rel
        )

        qs = ClientGroupAndAggregate.group_and_aggregate(
            query,
            [
                (
                    'discount_amount',
                    func.sum(OrderItem.discount_amount / 100)
                ),
            ]
        )

        return qs.all()

    @staticmethod
    def get_refunds(
        kpi_selector: KPISelector,
        business: Business,
        dt_from: datetime,
        dt_to: datetime,
        order_rel
    ):
        query, ok = kpi_selector.pms_refunds.orderitem_with_all_filters(
            business,
            dt_from,
            dt_to,
            order_rel=order_rel
        )

        qs = ClientGroupAndAggregate.group_and_aggregate(
            query,
            [
                (
                    'refund_amount',
                    func.sum(OrderItem.amount / 100)
                ),
            ]
        )

        return qs.all()


class NetRevenueERP(BaseKPICalculation):

    def calculate(self, db: session.Session, dt: date):
        for provider in db.query(Provider):
            yield InternalKPIValue(
                data_source=KPIDataSource.ERP,
                kind=KPIKind.FINANCIAL_NET_REVENUE,
                value=0,
                date=dt,
                corporation_id=provider.business.corporation_id,
                business_id=provider.business_id,
                provider_id=provider.id,
                # revenue_center_id=transaction.revenue_center_id,
                # department_id=transaction.department_id,
                # class_id=transaction.class_id
            )
