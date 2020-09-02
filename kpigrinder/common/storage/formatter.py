import typing

from ghostdb.db.models.kpi import AbstactKPIValue


class UnkonwnObjectFormatterException(Exception):
    ...


class BigQueryFormatter:

    @classmethod
    def format(cls, obj: typing.Any):
        if isinstance(obj, AbstactKPIValue):
            return cls._kpi_value(obj)

        raise UnkonwnObjectFormatterException(
            'BigQuery Formatter doesn\'t suppoer formatting objects of type: {}'.format(
                type(obj)
            )
        )

    @staticmethod
    def _kpi_value(val: AbstactKPIValue):
        return {
            'data_source': val.data_source.name,
            'kind': val.kind.name,
            'date': val.date.isoformat(),
            'corporation': val.corporation.name,
            'business': val.business.name,
            'provider': val.provider.full_name if val.provider else None,
            'client': val.client.full_name if val.client else None,
            'pet': val.pet.name if val.pet else None,
            'value': float(val.value),
            # 'revenue_center': val.revenue_center.name if val.revenue_center else None,
            # 'department': val.department.name if val.department else None,
            # 'category': val.category.name if val.category else None,
            # 'class': val.klass.name if val.klass else None,
            # 'subclass': val.subclass.name if val.subclass else None,
            # 'servicetype': val.servicetype.name if val.servicetype else None,
            'corporation_id': val.corporation_id.hex,
            'business_id': val.business_id.hex,
            'provider_id': val.provider_id.hex if val.provider_id else None,
            'client_id': val.client_id.hex if val.client_id else None,
            'pet_id': val.pet_id.hex if val.pet_id else None,
        }
