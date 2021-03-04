import uuid
from datetime import date
from unittest.mock import Mock

from ghostdb.db.models.corporation import Corporation
from ghostdb.db.models.kpi import KPIKind, KPIDataSource
from ghostdb.db.models.tests.factories import CorporationFactory, BusinessFactory, ProviderFactory
from kpigrinder.calculators.finance.ebitda import EbitdaERP, Ebitda


class TestAccountsReceivableERP:

    def test_basic_calculation(self, dbsession, monkeypatch):
        dt = date(2020, 6, 10)
        corp = CorporationFactory()
        business = BusinessFactory(corporation=corp)
        provider_1 = ProviderFactory(business=business)
        provider_2 = ProviderFactory(business=business)

        kpi_calculator = EbitdaERP([]).calculate(dbsession, dt)

        result = {
            (value.data_source, value.kind, value.provider_id, value.date, value.value)
            for value in kpi_calculator
        }
        expected_result = {
            (KPIDataSource.ERP, KPIKind.FINANCIAL_EBITDA, provider_1.id, dt, 0),
            (KPIDataSource.ERP, KPIKind.FINANCIAL_EBITDA, provider_2.id, dt, 0),
        }

        assert result == expected_result


class TestEbitda:

    def test_basic_calculation(self, monkeypatch):
        m_get_corporations = Mock(return_value={'test-customer': 1})
        m_bq_client = Mock()
        m_bq_stor = Mock()

        monkeypatch.setattr(Ebitda, 'get_corporations', m_get_corporations)
        monkeypatch.setattr(Ebitda, 'get_bigquery_client', Mock(return_value=m_bq_client))

        m_bq_result = Mock()
        m_bq_client.query.return_value = m_bq_result
        m_bq_result.result.return_value = (
            {
                'ebitda': 5,
                'customer_name': 'Test-Customer',
                'name': 'test-name',
                'source_id': 123,
                'country': 'us',
                'city': 'Neligh',
                'state': 'NE',
            },
        )

        dt = date(2021, 2, 28)
        kpi = Ebitda([m_bq_stor])
        for item in kpi.calculate(db=None, dt=dt):
            assert item == {
                'data_source': KPIDataSource.ERP.value,
                'kind': KPIKind.FINANCIAL_EBITDA.value,
                'value': 5,
                'date': dt.isoformat(),
                'corporation': 'Test-Customer',
                'corporation_id': 1,
                'business': 'test-name',
                'business_id': 123,
                'country': 'us',
                'city': 'Neligh',
                'state': 'NE',
            }

    def test_get_corporations(self, monkeypatch):
        c1_id = uuid.uuid4()
        c2_id = uuid.uuid4()

        m_db_query = Mock(**{'values.return_value': (
            ('Corp1', c1_id),
            ('Corp2', c2_id),
        )})
        m_db = Mock(**{'query.return_value': m_db_query})

        kpi = Ebitda([])
        assert kpi.get_corporations(m_db) == {
            'corp1': c1_id.hex,
            'corp2': c2_id.hex,
        }
        m_db.query.assert_called_once_with(Corporation)
        m_db_query.values.assert_called_once_with(Corporation.name, Corporation.id)
