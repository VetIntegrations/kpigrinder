from datetime import date

from ghostdb.db.models.kpi import KPIKind, KPIDataSource
from ghostdb.db.models.tests.factories import (
     CorporationFactory, BusinessFactory, ProviderFactory, ClientFactory, PetFactory, PaymentFactory
)
from kpigrinder.calculators.finance.cogs import CogsPMS, CogsERP


class TestCogsPMS:

    def test_basic_calculations(self, dbsession):
        dt = date(2020, 6, 10)
        corp = CorporationFactory()

        business_1 = BusinessFactory(corporation=corp)
        business_2 = BusinessFactory(corporation=corp)

        provider_1 = ProviderFactory(business=business_1)
        provider_2 = ProviderFactory(business=business_1)
        provider_3 = ProviderFactory(business=business_2)

        client_1 = ClientFactory()
        client_2 = ClientFactory()
        client_3 = ClientFactory()

        pet_1 = PetFactory()
        pet_2 = PetFactory()
        pet_3 = PetFactory()

        PaymentFactory(
            corporation=corp,
            business=business_1,
            provider=provider_1,
            client_id=client_1.id,
            pet_id=pet_1.id,
            value=100,
            date=dt,
        )
        PaymentFactory(
            corporation=corp,
            business=business_1,
            provider=provider_1,
            client_id=client_2.id,
            pet_id=pet_2.id,
            value=100,
            date=dt,
        )
        PaymentFactory(
            corporation=corp,
            business=business_1,
            provider=provider_1,
            client_id=client_3.id,
            pet_id=pet_3.id,
            value=100,
            date=dt,
        )
        PaymentFactory(
            corporation=corp,
            business=business_1,
            provider=provider_2,
            client_id=client_1.id,
            pet_id=pet_1.id,
            value=100,
            date=dt,
        )
        PaymentFactory(
            corporation=corp,
            business=business_1,
            provider=provider_2,
            client_id=client_2.id,
            pet_id=pet_2.id,
            value=100,
            date=dt,
        )
        PaymentFactory(
            corporation=corp,
            business=business_2,
            provider=provider_3,
            client_id=client_1.id,
            pet_id=pet_1.id,
            value=100,
            date=dt,
        )

        kpi_calculator = CogsPMS([]).calculate(dbsession, dt)

        result = {
            (value.data_source, value.kind, value.provider_id, value.date, value.value)
            for value in kpi_calculator
        }
        expected_result = {
            (KPIDataSource.PIMS, KPIKind.FINANCIAL_COGS, provider_1.id, dt, 100 + 100 + 100),
            (KPIDataSource.PIMS, KPIKind.FINANCIAL_COGS, provider_2.id, dt, 100 + 100),
            (KPIDataSource.PIMS, KPIKind.FINANCIAL_COGS, provider_3.id, dt, 100),
        }

        assert result == expected_result


class TestCogsERP:

    def test_basic_calculation(self, dbsession, monkeypatch):
        dt = date(2020, 6, 10)
        corp = CorporationFactory()
        business = BusinessFactory(corporation=corp)
        provider_1 = ProviderFactory(business=business)
        provider_2 = ProviderFactory(business=business)

        kpi_calculator = CogsERP([]).calculate(dbsession, dt)

        result = {
            (value.data_source, value.kind, value.provider_id, value.date, value.value)
            for value in kpi_calculator
        }
        expected_result = {
            (KPIDataSource.ERP, KPIKind.FINANCIAL_COGS, provider_1.id, dt, 0),
            (KPIDataSource.ERP, KPIKind.FINANCIAL_COGS, provider_2.id, dt, 0),
        }

        assert result == expected_result
