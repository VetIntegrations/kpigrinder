from .finance import net_profit, net_revenue, accounts_receivable, cogs, ebitda


class KPIRegistry:

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

    @classmethod
    def get_classes_path(cls):
        for klass in cls.CLASSES:
            yield '{}.{}'.format(klass.__module__, klass.__name__)
