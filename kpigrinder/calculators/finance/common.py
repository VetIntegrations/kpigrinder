from datetime import datetime
from sqlalchemy import func

from ghostdb.bl.selectors.kpi import KPISelector
from ghostdb.db.models.business import Business
from ghostdb.db.models.order import OrderItem
from kpigrinder.calculators.utils import BaseGroupAndAggregate


def get_gross_revenue(
    kpi_selector: KPISelector,
    business: Business,
    dt_from: datetime,
    dt_to: datetime,
    order_rel,
    group_and_aggregation: BaseGroupAndAggregate
):
    query, ok = kpi_selector.pms_gross_revenue.orderitem_with_all_filters(
        business,
        dt_from,
        dt_to,
        order_rel=order_rel
    )

    qs = group_and_aggregation.group_and_aggregate(
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
