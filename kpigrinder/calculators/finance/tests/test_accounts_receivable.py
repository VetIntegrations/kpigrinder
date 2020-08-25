from datetime import date

from ghostdb.db.models.kpi import KPIKind, KPIDataSource
from ghostdb.db.models.tests.factories import CorporationFactory, BusinessFactory, ProviderFactory
from kpigrinder.calculators.finance.accounts_receivable import AccountsReceivableERP


class TestAccountsReceivableERP:

    def test_basic_calculation(self, dbsession, monkeypatch):
        dt = date(2020, 6, 10)
        corp = CorporationFactory()
        business = BusinessFactory(corporation=corp)
        provider_1 = ProviderFactory(business=business)
        provider_2 = ProviderFactory(business=business)

        kpi_calculator = AccountsReceivableERP([]).calculate(dbsession, dt)

        result = {
            (value.data_source, value.kind, value.provider_id, value.date, value.value)
            for value in kpi_calculator
        }
        expected_result = {
            (KPIDataSource.ERP, KPIKind.FINANCIAL_ACCOUNTS_RECEIVABLE, provider_1.id, dt, 0),
            (KPIDataSource.ERP, KPIKind.FINANCIAL_ACCOUNTS_RECEIVABLE, provider_2.id, dt, 0),
        }

        assert result == expected_result
