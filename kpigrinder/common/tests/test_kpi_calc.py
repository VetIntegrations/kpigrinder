from datetime import date
from unittest.mock import Mock

from kpigrinder.common.kpi_calc import BaseKPICalculation


class KPICalculation(BaseKPICalculation):

    def calculate(self, db, dt):
        yield 1


class TestBaseKPICalculation:

    def test_get_storages(self):
        storages = ('Storage1', 2, )
        kpi_calc = KPICalculation(storages)

        assert kpi_calc.get_storages() == storages

    def test_store(self):
        storage1 = Mock()
        storage2 = Mock()

        obj = {'name': 'SomeName', 'value': 3.14}

        kpi_calc = KPICalculation([storage1, storage2])
        kpi_calc.store(obj)

        storage1.store.assert_called_once_with(obj)
        storage2.store.assert_called_once_with(obj)

    def test_get_db_uri(self):
        kpi_calc = KPICalculation([])

        credentials = {
            'conn_type': 'gdb',
            'login': 'test',
            'password': 'T3st',
            'host': 'localhost',
            'port': 1234,
            'schema': 'kpigrinder-test',
        }
        dsn = '{dbtype}://{login}:{password}@{host}:{port}/{schema}'.format(
            dbtype=credentials['conn_type'],
            login=credentials['login'],
            password=credentials['password'],
            host=credentials['host'],
            port=credentials['port'],
            schema=credentials['schema']
        )

        assert kpi_calc.get_db_uri(credentials) == dsn

    def test_process(self, monkeypatch):
        dbsession = Mock()
        storage = Mock()

        credentials = {
            'conn_type': 'gdb',
            'login': 'test',
            'password': 'T3st',
            'host': 'localhost',
            'port': 1234,
            'schema': 'kpigrinder-test',
        }
        kpi_calc = KPICalculation([storage])
        monkeypatch.setattr(kpi_calc, 'get_db_connection', lambda uri: dbsession)
        monkeypatch.setattr(kpi_calc, 'get_credentials', lambda name: credentials)

        kpi_calc.process(date.today())

        storage.store.assert_called_once_with(1)
