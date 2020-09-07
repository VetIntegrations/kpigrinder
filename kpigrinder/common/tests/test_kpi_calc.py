import pytz
import pytest
from datetime import date, datetime, timedelta
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
        monkeypatch.setattr(kpi_calc, 'need_to_be_stored', lambda kpi_value: True)

        kpi_calc.process(date.today())

        storage.store.assert_called_once_with(1)

    @pytest.mark.parametrize(
        'need_to_be_stored_ret,store_called',
        (
            (True, True),
            (False, False)
        )
    )
    def test_process_check_for_needs_to_store(self, need_to_be_stored_ret, store_called, monkeypatch):
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
        monkeypatch.setattr(kpi_calc, 'need_to_be_stored', lambda kpi_value: need_to_be_stored_ret)

        kpi_calc.process(date.today())

        if store_called:
            storage.store.assert_called_once()
        else:
            storage.store.assert_not_called()

    @pytest.mark.parametrize(
        'value, expected_result',
        (
            (-1, True),
            (0, False),
            (1, True),
        )
    )
    def test_need_to_be_stored(self, value, expected_result):
        kpi_calc = KPICalculation([])
        assert kpi_calc.need_to_be_stored(Mock(value=value)) == expected_result

    @pytest.mark.parametrize(
        'tz',
        (
            'Europe/Paris',
            None
        )
    )
    def test_get_datetime_range_with_time_zone(self, tz):

        kpi_calc = KPICalculation([])
        dt = date(2020, 9, 3)

        test_dt_from = datetime.combine(dt, datetime.min.time())
        test_dt_to = test_dt_from + timedelta(days=1)

        dt_from, dt_to = kpi_calc.get_datetime_range_with_time_zone(dt, tz=tz)
        if tz:
            test_dt_from = pytz.timezone(tz).localize(test_dt_from)
            test_dt_to = pytz.timezone(tz).localize(test_dt_to)

        assert dt_from == test_dt_from
        assert dt_to == test_dt_to

    def test_get_datetime_range_with_time_zone__timedelta_default(self):

        kpi_calc = KPICalculation([])
        dt = date(2020, 9, 3)

        test_dt_from = datetime.combine(dt, datetime.min.time())

        # timedelta is default
        dt_from, dt_to = kpi_calc.get_datetime_range_with_time_zone(dt, tz=None)
        assert dt_from == test_dt_from
        assert dt_to == test_dt_from + timedelta(days=1)

        # timedelta is 30 days
        dt_from, dt_to = kpi_calc.get_datetime_range_with_time_zone(dt, tz=None, time_delta=timedelta(days=30))
        assert dt_from == test_dt_from
        assert dt_to == test_dt_from + timedelta(days=30)
