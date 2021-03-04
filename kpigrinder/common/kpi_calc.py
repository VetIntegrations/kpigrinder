import abc
import pytz
import logging
import typing
from datetime import date, datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, session

from ghostdb.db.models import kpi as kpi_models
from kpigrinder import config
from kpigrinder.common.storage import ghostdb, bigquery
from kpigrinder.utils.secret_manager import SecretManager


logger = logging.getLogger('kpigrinder')


class KPICalculationInterface(abc.ABC):

    def __init__(self):
        ...

    @abc.abstractmethod
    def process(self, dt: date):
        ...

    @abc.abstractmethod
    def store(self, kpi_value: kpi_models.AbstactKPIValue):
        ...

    @abc.abstractmethod
    def calculate(self, db: session.Session, dt: date):
        ...

    @staticmethod
    @abc.abstractmethod
    def get_credentials(name: str):
        ...

    @abc.abstractmethod
    def need_to_be_stored(self, kpi_value: kpi_models.AbstactKPIValue):
        ...

    @staticmethod
    @abc.abstractmethod
    def get_datetime_range_with_time_zone(
        dt: date,
        tz: [str, None],
        time_delta: timedelta
    ) -> typing.Tuple[datetime, datetime]:
        ...


class BaseKPICalculation(KPICalculationInterface):

    def __init__(self, storages: typing.Iterable):
        super().__init__()
        self._storages = storages

    def process(self, db: session.Session, dt: date, query_filter: dict = None):
        db = self.get_db_connection(
            self.get_db_uri(self.get_credentials(config.CONNECTION_GHOSTDB))
        )

        for kpi_value in self.calculate(db, dt):
            if self.need_to_be_stored(kpi_value):
                self.store(kpi_value)

    def get_storages(self):
        return self._storages

    def need_to_be_stored(self, kpi_value: kpi_models.AbstactKPIValue):
        value = None
        if isinstance(kpi_value, dict):
            value = kpi_value['value']
        else:
            value = kpi_value.value
        return bool(value)

    def store(self, kpi_value: kpi_models.AbstactKPIValue):
        for storage in self.get_storages():
            storage.store(kpi_value)

    def get_ghostdb_client(self):
        for storage in self._storages:
            if isinstance(storage, ghostdb.GhostDBStorage):
                return storage.get_connection()

    def get_bigquery_client(self):
        for storage in self._storages:
            if isinstance(storage, bigquery.BigQueryStorage):
                return storage.get_connection()

    @staticmethod
    def get_db_uri(credentials: dict) -> str:
        return '{dbtype}://{login}:{password}@{host}:{port}/{schema}'.format(
            dbtype=credentials['conn_type'],
            login=credentials['login'],
            password=credentials['password'],
            host=credentials['host'],
            port=credentials['port'],
            schema=credentials['schema']
        )

    @staticmethod
    def get_db_connection(uri: str) -> session.Session:
        engine = create_engine(uri)
        db = sessionmaker(bind=engine)

        return db()

    @staticmethod
    def get_credentials(name: str):
        sm = SecretManager()

        return sm.get_secret(name)

    @staticmethod
    def get_datetime_range_with_time_zone(
        dt: date,
        tz: [str, None],
        time_delta: timedelta = timedelta(days=1)
    ) -> typing.Tuple[datetime, datetime]:
        dt_from = datetime.combine(dt, datetime.min.time())
        dt_to = dt_from + time_delta
        if tz:
            dt_from = pytz.timezone(tz).localize(dt_from)
            dt_to = pytz.timezone(tz).localize(dt_to)

        return dt_from, dt_to
