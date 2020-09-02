import abc

from .finance import net_profit, net_revenue, accounts_receivable, cogs, ebitda
from . import external_kpis


class AbstractKPIRegistry(abc.ABC):

    CLASSES = tuple()

    @classmethod
    def get_classes_path(cls):
        for klass in cls.CLASSES:
            yield '{}.{}'.format(klass.__module__, klass.__name__)


class InternalKPIRegistry(AbstractKPIRegistry):

    CLASSES = (
        net_profit.NetProfitPMS,
        net_profit.NetProfitERP,
        net_revenue.NetRevenuePMS,
        net_revenue.NetRevenueERP,
        accounts_receivable.AccountsReceivableERP,
        cogs.CogsPMS,
        cogs.CogsERP,
        ebitda.EbitdaERP,
    )


class ExternalKPIRegistry(AbstractKPIRegistry):

    CLASSES = (
        external_kpis.GenericExternalKPICalculation,
    )
