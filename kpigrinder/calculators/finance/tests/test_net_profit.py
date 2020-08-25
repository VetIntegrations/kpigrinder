from datetime import date
from decimal import Decimal

from ghostdb.db.models.kpi import KPIKind, KPIDataSource
from ghostdb.db.models.order import OrderStatus
from ghostdb.db.models.tests.factories import (
    CorporationFactory, BusinessFactory, ProviderFactory, OrderFactory, OrderItemFactory
)
from kpigrinder.calculators.finance.net_profit import NetProfitPMS, NetProfitERP


class TestNetProfitPMS:

    def test_basic_calculation(self, dbsession):
        dt = date(2020, 6, 21)
        corp = CorporationFactory()
        business = BusinessFactory(corporation=corp)
        provider_1 = ProviderFactory(business=business)
        order1 = OrderFactory(corporation=corp, business=business, provider=provider_1, status=OrderStatus.DUE)
        # here we should use amount
        OrderItemFactory(order=order1, amount=520, description='', date=dt)
        # here we should use quantity and unit_price
        OrderItemFactory(order=order1, quantity=100, unit_price=12.45, amount=500, description='', date=dt)
        OrderItemFactory(
            order=order1, quantity=100, unit_price=3.45, amount=500, is_inventory=True, description='', date=dt
        )

        kpi_calculator = NetProfitPMS([]).calculate(dbsession, dt)

        result = {
            (value.data_source, value.kind, value.provider_id, value.date, value.value.quantize(Decimal('.01')))
            for value in kpi_calculator
        }
        expected_result = {
            (
                KPIDataSource.PIMS,
                KPIKind.FINANCIAL_NET_PROFIT,
                provider_1.id,
                dt,
                Decimal((520 + 12.45 * 100 - 3.45 * 100) / 100.).quantize(Decimal('.01'))
            ),
        }

        assert result == expected_result

    def test_basic_calculation_without_inventory_records(self, dbsession):
        dt = date(2020, 6, 21)
        corp = CorporationFactory()
        business = BusinessFactory(corporation=corp)
        provider_1 = ProviderFactory(business=business)
        order1 = OrderFactory(corporation=corp, business=business, provider=provider_1, status=OrderStatus.DUE)
        # here we should use amount
        OrderItemFactory(order=order1, amount=520, description='', date=dt)
        # here we should use quantity and unit_price
        OrderItemFactory(order=order1, quantity=100, unit_price=12.45, amount=500, description='', date=dt)

        kpi_calculator = NetProfitPMS([]).calculate(dbsession, dt)

        result = {
            (value.data_source, value.kind, value.provider_id, value.date, value.value.quantize(Decimal('.01')))
            for value in kpi_calculator
        }
        expected_result = {
            (
                KPIDataSource.PIMS,
                KPIKind.FINANCIAL_NET_PROFIT,
                provider_1.id,
                dt,
                Decimal((520 + 12.45 * 100) / 100.).quantize(Decimal('.01'))
            ),
        }

        assert result == expected_result

    def test_split_by_provider(self, dbsession):
        dt = date(2020, 6, 21)
        corp = CorporationFactory()
        business = BusinessFactory(corporation=corp)
        provider_1 = ProviderFactory(business=business)
        order1 = OrderFactory(corporation=corp, business=business, provider=provider_1, status=OrderStatus.DUE)
        # here we should use amount
        OrderItemFactory(order=order1, amount=520, description='', date=dt)
        # here we should use quantity and unit_price
        OrderItemFactory(order=order1, quantity=100, unit_price=12.45, amount=500, description='', date=dt)
        OrderItemFactory(
            order=order1, quantity=100, unit_price=3.45, amount=500, is_inventory=True, description='', date=dt
        )
        provider_2 = ProviderFactory(business=business)
        order2 = OrderFactory(corporation=corp, business=business, provider=provider_2, status=OrderStatus.DUE)
        # here we should use amount
        OrderItemFactory(order=order2, amount=320, description='', date=dt)
        # here we should use quantity and unit_price
        OrderItemFactory(order=order2, quantity=100, unit_price=7.45, amount=500, description='', date=dt)
        OrderItemFactory(
            order=order2, quantity=100, unit_price=1.45, amount=500, is_inventory=True, description='', date=dt
        )

        kpi_calculator = NetProfitPMS([]).calculate(dbsession, dt)

        result = {
            (value.data_source, value.kind, value.provider_id, value.date, value.value.quantize(Decimal('.01')))
            for value in kpi_calculator
        }
        expected_result = {
            (
                KPIDataSource.PIMS,
                KPIKind.FINANCIAL_NET_PROFIT,
                provider_1.id,
                dt,
                Decimal((520 + 12.45 * 100 - 3.45 * 100) / 100.).quantize(Decimal('.01'))
            ),
            (
                KPIDataSource.PIMS,
                KPIKind.FINANCIAL_NET_PROFIT,
                provider_2.id,
                dt,
                Decimal((320 + 7.45 * 100 - 1.45 * 100) / 100.).quantize(Decimal('.01'))
            ),
        }

        assert result == expected_result

    def test_combine_orders(self, dbsession):
        dt = date(2020, 6, 21)
        corp = CorporationFactory()
        business = BusinessFactory(corporation=corp)
        provider_1 = ProviderFactory(business=business)
        order1 = OrderFactory(corporation=corp, business=business, provider=provider_1, status=OrderStatus.DUE)
        # here we should use amount
        OrderItemFactory(order=order1, amount=520, description='', date=dt)
        # here we should use quantity and unit_price
        OrderItemFactory(order=order1, quantity=100, unit_price=12.45, amount=500, description='', date=dt)
        OrderItemFactory(
            order=order1, quantity=100, unit_price=3.45, amount=500, is_inventory=True, description='', date=dt
        )
        order2 = OrderFactory(corporation=corp, business=business, provider=provider_1, status=OrderStatus.DUE)
        OrderItemFactory(order=order2, amount=115, description='', date=dt)

        kpi_calculator = NetProfitPMS([]).calculate(dbsession, dt)

        result = {
            (value.data_source, value.kind, value.provider_id, value.date, value.value.quantize(Decimal('.01')))
            for value in kpi_calculator
        }
        expected_result = {
            (
                KPIDataSource.PIMS,
                KPIKind.FINANCIAL_NET_PROFIT,
                provider_1.id,
                dt,
                Decimal((520 + 12.45 * 100 - 3.45 * 100 + 115) / 100.).quantize(Decimal('.01'))
            ),
        }

        assert result == expected_result


class TestNetProfitERP:

    def test_basic_calculation(self, dbsession, monkeypatch):
        dt = date(2020, 6, 10)
        corp = CorporationFactory()
        business = BusinessFactory(corporation=corp)
        provider_1 = ProviderFactory(business=business)
        provider_2 = ProviderFactory(business=business)

        kpi_calculator = NetProfitERP([]).calculate(dbsession, dt)

        result = {
            (value.data_source, value.kind, value.provider_id, value.date, value.value)
            for value in kpi_calculator
        }
        expected_result = {
            (KPIDataSource.ERP, KPIKind.FINANCIAL_NET_PROFIT, provider_1.id, dt, 0),
            (KPIDataSource.ERP, KPIKind.FINANCIAL_NET_PROFIT, provider_2.id, dt, 0),
        }

        assert result == expected_result
