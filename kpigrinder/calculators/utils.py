from sqlalchemy.sql import label
from sqlalchemy.orm.util import aliased


class BaseGroupAndAggregate:

    @classmethod
    def key_builder(cls, obj):
        return '-'.join([
            str(getattr(obj, entity_data[1]))
            for entity_data in cls.get_entities()
        ])

    @classmethod
    def group_and_aggregate(cls, query, additional_aggregations=None):
        rels = {}
        entities = []
        groupby = []
        for entity_data in cls.get_entities():
            model, _label, field_name = entity_data[0], entity_data[1], entity_data[1]
            if len(entity_data) > 2:
                _label = entity_data[2]

            if model not in rels:
                rels[model] = aliased(model)

            entities.append(label(_label, getattr(rels[model], field_name)))
            groupby.append(getattr(rels[model], field_name))

        if additional_aggregations:
            for aggregation in additional_aggregations:
                entities.append(label(*aggregation))

        for rel in rels.values():
            query = query.outerjoin(rel)

        return query.with_entities(*entities).group_by(*groupby)

    @staticmethod
    def get_entities():
        ...


class GeneralGroupAndAggregate(BaseGroupAndAggregate):

    @staticmethod
    def get_entities():
        from ghostdb.db.models.code import Service
        from ghostdb.db.models.order import Order

        return [
            (Order, 'corporation_id', ),
            (Order, 'business_id', ),
            (Order, 'provider_id', ),

            (Service, 'revenue_center_id', ),
            (Service, 'department_id', ),
            (Service, 'category_id', ),
            (Service, 'class_id', ),
            (Service, 'subclass_id'),
            (Service, 'servicetype_id'),
        ]


class ClientGroupAndAggregate(GeneralGroupAndAggregate):

    @classmethod
    def get_entities(cls):
        from ghostdb.db.models.order import Order

        entities = super().get_entities()

        entities.insert(3, (Order, 'client_id'))

        return entities
