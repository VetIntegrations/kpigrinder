import pytest
from datetime import date, timedelta
from unittest.mock import Mock, call

from kpigrinder.tasks import kpi


class TestRunAllKPICalculation:

    def test_no_params(self, monkeypatch):
        """should run calculations just for previous date"""
        kpi_registry = Mock(**{'get_classes_path.return_value': ('test.kpi_calc', )})
        kpi_calc = Mock()
        monkeypatch.setattr(kpi, 'KPIRegistry', kpi_registry)
        monkeypatch.setattr(kpi, 'kpi_calculate', kpi_calc)

        kpi.run_all_kpi_calculation()
        kpi_calc.delay.assert_called_once_with(
            kpi_class_path='test.kpi_calc',
            dt=date.today() - timedelta(days=1)
        )

    def test_params_only_start_date(self, monkeypatch):
        """should run calculations from start date until today"""
        kpi_registry = Mock(**{'get_classes_path.return_value': ('test.kpi_calc', )})
        kpi_calc = Mock()
        monkeypatch.setattr(kpi, 'KPIRegistry', kpi_registry)
        monkeypatch.setattr(kpi, 'kpi_calculate', kpi_calc)

        date_start = date(2020, 5, 15)
        kpi.run_all_kpi_calculation(date_start)
        kpi_calc.delay.assert_has_calls([
            call(kpi_class_path='test.kpi_calc', dt=date_start + timedelta(days=days))
            for days in range((date.today() - date_start).days)
        ])

    def test_params_start_and_end_date(self, monkeypatch):
        """should run calculations just in range of given dates"""
        kpi_registry = Mock(**{'get_classes_path.return_value': ('test.kpi_calc', )})
        kpi_calc = Mock()
        monkeypatch.setattr(kpi, 'KPIRegistry', kpi_registry)
        monkeypatch.setattr(kpi, 'kpi_calculate', kpi_calc)

        date_start = date(2020, 5, 15)
        date_end = date(2020, 5, 20)
        kpi.run_all_kpi_calculation(date_start, date_end)
        kpi_calc.delay.assert_has_calls([
            call(kpi_class_path='test.kpi_calc', dt=date_start + timedelta(days=days))
            for days in range((date_end - date_start).days)
        ])

    def test_params_end_date_less_then_start(self, monkeypatch):
        with pytest.raises(kpi.TaskParamException):
            kpi.run_all_kpi_calculation(date(2020, 5, 15), date(2020, 5, 10))
