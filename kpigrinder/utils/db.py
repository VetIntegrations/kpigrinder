import threading
from celery.signals import worker_process_init, worker_process_shutdown
from sqlalchemy import orm, create_engine

from kpigrinder import config
from .secret_manager import SecretManager


db_session = orm.scoped_session(orm.sessionmaker(), scopefunc=threading.get_ident)


class DBAppTaskMixin:
    _db = None

    @property
    def db(self):
        if not self._db:
            self._db = db_session()

        return self._db


@worker_process_init.connect
def db_connection(**kwargs):
    engine = get_db_engine(get_db_credentials())
    connection = engine.connect()
    db_session.configure(bind=connection)


@worker_process_shutdown.connect
def db_disconnect(**kwargs):
    db_session.close()


def get_db_credentials():
    sm = SecretManager()
    return sm.get_secret(config.CONNECTION_GHOSTDB)


def get_dsn_from_db_credentials(credentials: dict):
    return '{dbtype}://{login}:{password}@{host}:{port}/{schema}'.format(
        dbtype=credentials['conn_type'],
        login=credentials['login'],
        password=credentials['password'],
        host=credentials['host'],
        port=credentials['port'],
        schema=credentials['schema']
    )


def get_db_engine(credentials: dict):
    dsn = get_dsn_from_db_credentials(credentials)
    engine = create_engine(
        dsn,
        pool_size=config.DB_POOL_SIZE,
        max_overflow=config.DB_MAX_OVERFLOW
    )

    return engine
