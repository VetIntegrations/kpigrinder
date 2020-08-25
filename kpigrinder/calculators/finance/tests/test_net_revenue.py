from datetime import datetime, date, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, call
from sqlalchemy import func
from sqlalchemy.orm.util import aliased

from ghostdb.db.models.business import Business
from ghostdb.db.models.kpi import KPIKind, KPIDataSource
from ghostdb.db.models.order import Order, OrderItem, OrderStatus
from ghostdb.db.models.tests.factories import (
    CorporationFactory, BusinessFactory, ProviderFactory, ClientFactory, OrderFactory, OrderItemFactory
)
from kpigrinder.calculators.finance.net_revenue import NetRevenuePMS, NetRevenueERP
from kpigrinder.calculators.utils import ClientGroupAndAggregate


def to_sql(statement):
    return str(statement.compile(compile_kwargs={"literal_binds": True}))


class TestNetRevenuePMS:

    def test_basic_calculation(self, dbsession):

        dt = date(2020, 6, 10)
        corp = CorporationFactory()
        business = BusinessFactory(corporation=corp)
        provider_1 = ProviderFactory(business=business)
        client = ClientFactory()
        order1 = OrderFactory(
            corporation=corp, business=business, provider=provider_1, client=client, status=OrderStatus.DUE
        )

        # here we should use amount
        OrderItemFactory(order=order1, description="ANESTHESIA-TKX INJ.", amount=200, date=dt)

        # here we should use quantity and unit_price
        OrderItemFactory(
            order=order1, description="ANESTHESIA-TKX INJ.", quantity=100, unit_price=2.15, amount=125, date=dt
        )

        # here we should use discount
        OrderItemFactory(
            order=order1, description="Tumor Removal Large 7-10cm", amount=100, discount_amount=50, date=dt
        )

        # here we should use refund
        OrderItemFactory(order=order1, description="It's refundable", amount=-200, date=dt)

        kpi_calculator = NetRevenuePMS([]).calculate(dbsession, dt)

        result = {
            (value.data_source, value.kind, value.provider_id, value.date, value.value.quantize(Decimal('.01')))
            for value in kpi_calculator
        }
        expected_result = {
            (
                KPIDataSource.PIMS,
                KPIKind.FINANCIAL_NET_REVENUE,
                provider_1.id,
                dt,
                Decimal((200 + 2.15 * 100 + 100 - 50 - 200) / 100.).quantize(Decimal('.01'))
            ),
        }

        assert result == expected_result

    def test_get_discounts(self, dbsession, monkeypatch):
        corp = CorporationFactory()

        business_1 = BusinessFactory(corporation=corp)
        business_2 = BusinessFactory(corporation=corp)
        dbsession.add(business_1)
        dbsession.add(business_2)
        dbsession.commit()

        dt_from = datetime(2020, 6, 10, 10, 10)
        dt_to = dt_from + timedelta(days=1)

        mock_group_and_aggregate = MagicMock()

        # use Businesses items for test query
        mock_group_and_aggregate.side_effect = [
            dbsession.query(Business).filter(Business.id == business_1.id),
            dbsession.query(Business).filter(Business.id == business_2.id)
        ]

        monkeypatch.setattr(ClientGroupAndAggregate, 'group_and_aggregate', mock_group_and_aggregate)
        mock_selector = MagicMock(**{'pms_discount.orderitem_with_all_filters.side_effect': [
            ('test_query_1', True), ('test_query_2', True)
        ]})

        order_rel = aliased(Order)
        result_1 = NetRevenuePMS.get_discounts(mock_selector, business_1, dt_from, dt_to, order_rel)
        result_2 = NetRevenuePMS.get_discounts(mock_selector, business_2, dt_from, dt_to, order_rel)

        assert mock_selector.pms_discount.orderitem_with_all_filters.called
        assert mock_group_and_aggregate.called

        calls = [
            call(business_1, dt_from, dt_to, order_rel=order_rel),
            call(business_2, dt_from, dt_to, order_rel=order_rel),
        ]

        mock_selector.pms_discount.orderitem_with_all_filters.assert_has_calls(calls)

        test_aggregate_label = 'discount_amount'
        test_aggregate_expression = func.sum(OrderItem.discount_amount / 100)

        # test_aggregate_expression.compile(compile_kwargs={"literal_binds": True})
        call_1 = mock_group_and_aggregate.mock_calls[0][1]
        call_2 = mock_group_and_aggregate.mock_calls[1][1]

        assert call_1[0] == 'test_query_1'
        assert call_2[0] == 'test_query_2'

        assert len(call_1[1]) == 1
        assert (call_1[1][0][0], to_sql(call_1[1][0][1])) == (test_aggregate_label, to_sql(test_aggregate_expression))
        assert len(call_2[1]) == 1
        assert (call_2[1][0][0], to_sql(call_2[1][0][1])) == (test_aggregate_label, to_sql(test_aggregate_expression))

        assert result_1 == [business_1, ]
        assert result_2 == [business_2, ]

    def test_get_refunds(self, dbsession, monkeypatch):
        corp = CorporationFactory()

        business_1 = BusinessFactory(corporation=corp)
        business_2 = BusinessFactory(corporation=corp)
        dbsession.add(business_1)
        dbsession.add(business_2)
        dbsession.commit()

        dt_from = datetime(2020, 6, 10, 10, 10)
        dt_to = dt_from + timedelta(days=1)

        mock_group_and_aggregate = MagicMock()

        # use Businesses items for test query
        mock_group_and_aggregate.side_effect = [
            dbsession.query(Business).filter(Business.id == business_1.id),
            dbsession.query(Business).filter(Business.id == business_2.id)
        ]

        monkeypatch.setattr(ClientGroupAndAggregate, 'group_and_aggregate', mock_group_and_aggregate)
        mock_selector = MagicMock(**{'pms_refunds.orderitem_with_all_filters.side_effect': [
            ('test_query_1', True), ('test_query_2', True)
        ]})

        order_rel = aliased(Order)
        result_1 = NetRevenuePMS.get_refunds(mock_selector, business_1, dt_from, dt_to, order_rel)
        result_2 = NetRevenuePMS.get_refunds(mock_selector, business_2, dt_from, dt_to, order_rel)

        assert mock_selector.pms_refunds.orderitem_with_all_filters.called
        assert mock_group_and_aggregate.called

        calls = [
            call(business_1, dt_from, dt_to, order_rel=order_rel),
            call(business_2, dt_from, dt_to, order_rel=order_rel),
        ]

        mock_selector.pms_refunds.orderitem_with_all_filters.assert_has_calls(calls)

        test_aggregate_label = 'refund_amount'
        test_aggregate_expression = func.sum(OrderItem.amount / 100)

        # test_aggregate_expression.compile(compile_kwargs={"literal_binds": True})
        call_1 = mock_group_and_aggregate.mock_calls[0][1]
        call_2 = mock_group_and_aggregate.mock_calls[1][1]

        assert call_1[0] == 'test_query_1'
        assert call_2[0] == 'test_query_2'

        assert len(call_1[1]) == 1
        assert (call_1[1][0][0], to_sql(call_1[1][0][1])) == (test_aggregate_label, to_sql(test_aggregate_expression))
        assert len(call_2[1]) == 1
        assert (call_2[1][0][0], to_sql(call_2[1][0][1])) == (test_aggregate_label, to_sql(test_aggregate_expression))

        assert result_1 == [business_1, ]
        assert result_2 == [business_2, ]


class TestNetRevenueERP:

    def test_basic_calculation(self, dbsession, monkeypatch):
        dt = date(2020, 6, 10)
        corp = CorporationFactory()
        business = BusinessFactory(corporation=corp)
        provider_1 = ProviderFactory(business=business)
        provider_2 = ProviderFactory(business=business)

        kpi_calculator = NetRevenueERP([]).calculate(dbsession, dt)

        result = {
            (value.data_source, value.kind, value.provider_id, value.date, value.value)
            for value in kpi_calculator
        }
        expected_result = {
            (KPIDataSource.ERP, KPIKind.FINANCIAL_NET_REVENUE, provider_1.id, dt, 0),
            (KPIDataSource.ERP, KPIKind.FINANCIAL_NET_REVENUE, provider_2.id, dt, 0),
        }

        assert result == expected_result
