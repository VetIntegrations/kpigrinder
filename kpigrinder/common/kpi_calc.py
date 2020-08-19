import abc
import logging
import typing
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, session

from ghostdb.db.models import kpi as kpi_models
from kpigrinder import config
from kpigrinder.utils.secret_manager import SecretManager


logger = logging.getLogger('kpigrinder')


class KPICalculationInterface(abc.ABC):

    def __init__(self):
        ...

    @abc.abstractmethod
    def process(self, dt: date):
        ...

    @abc.abstractmethod
    def store(self, kpi_value: kpi_models.KPIValue):
        ...

    @abc.abstractmethod
    def calculate(self, db: session.Session, dt: date):
        ...

    @abc.abstractmethod
    def get_credentials(self, name: str):
        ...


class BaseKPICalculation(KPICalculationInterface):

    def __init__(self, storages: typing.Iterable):
        super().__init__()
        self._storages = storages

    def process(self, dt: date, query_filter: dict = None):
        db = self.get_db_connection(
            self.get_db_uri(self.get_credentials(config.CONNECTION_GHOSTDB))
        )

        for kpi_value in self.calculate(db, dt):
            for storage in self._storages:
                storage.store(kpi_value)

    def get_storages(self):
        return self._storages

    def store(self, kpi_value: kpi_models.KPIValue):
        for storage in self.get_storages():
            storage.store(kpi_value)

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

    def get_credentials(self, name: str):
        sm = SecretManager()

        return sm.get_secret(name)
