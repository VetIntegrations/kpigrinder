import uuid
import pytest
from decimal import Decimal
from datetime import date
from unittest.mock import Mock

from ghostdb.db.models.kpi import InternalKPIValue, KPIDataSource, KPIKind
from kpigrinder.common.storage.formatter import BigQueryFormatter, UnkonwnObjectFormatterException


class TestBigQueryFormatter_General:

    def test_exception_on_unknown_object(self):
        with pytest.raises(UnkonwnObjectFormatterException):
            BigQueryFormatter.format({})


class TestBigQueryFormatter_InternalKPIValue:

    def test_format_factory(self, monkeypatch):
        fmt_kpi_value = Mock()
        monkeypatch.setattr(BigQueryFormatter, '_kpi_value', fmt_kpi_value)

        kpi_value = InternalKPIValue()
        BigQueryFormatter.format(kpi_value)

        fmt_kpi_value.assert_called_once_with(kpi_value)

    def test_format_full_obj(self):
        kpi_value = InternalKPIValue(
            data_source=KPIDataSource.PIMS,
            kind=KPIKind.FINANCIAL_CAPEX,
            date=date(2020, 9, 12),
            corporation=Mock(name='TestCorp'),
            business=Mock(name='TestBusiness'),
            provider=Mock(full_name='TestProvider'),
            client=Mock(full_name='TestClient'),
            pet=Mock(name='TestPet'),
            value=Decimal('3.14'),
            corporation_id=uuid.uuid4(),
            business_id=uuid.uuid4(),
            provider_id=uuid.uuid4(),
            client_id=uuid.uuid4(),
            pet_id=uuid.uuid4(),
        )
        formatted = BigQueryFormatter.format(kpi_value)

        assert formatted == {
            'data_source': kpi_value.data_source.name,
            'kind': kpi_value.kind.name,
            'date': kpi_value.date.isoformat(),
            'corporation': kpi_value.corporation.name,
            'business': kpi_value.business.name,
            'provider': kpi_value.provider.full_name,
            'client': kpi_value.client.full_name,
            'pet': kpi_value.pet.name,
            'value': float(kpi_value.value),
            # 'revenue_center': kpi_value.revenue_center.name if kpi_value.revenue_center else None,
            # 'department': kpi_value.department.name if kpi_value.department else None,
            # 'category': kpi_value.category.name if kpi_value.category else None,
            # 'class': kpi_value.klass.name if kpi_value.klass else None,
            # 'subclass': kpi_value.subclass.name if kpi_value.subclass else None,
            # 'servicetype': kpi_value.servicetype.name if kpi_value.servicetype else None,
            'corporation_id': kpi_value.corporation_id.hex,
            'business_id': kpi_value.business_id.hex,
            'provider_id': kpi_value.provider_id.hex,
            'client_id': kpi_value.client_id.hex,
            'pet_id': kpi_value.pet_id,
        }
