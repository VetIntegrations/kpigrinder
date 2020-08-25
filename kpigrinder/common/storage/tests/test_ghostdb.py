from unittest.mock import Mock

from kpigrinder.common.storage import ghostdb
from kpigrinder.common.storage.ghostdb import GhostDBStorage


class TestGhostDBStorage:

    def test_connect_by_credentials(self, monkeypatch):
        engine = Mock()
        session = Mock()
        db = Mock(return_value=session)
        create_engine = Mock(return_value=engine)
        sessionmaker = Mock(return_value=db)

        monkeypatch.setattr(ghostdb, 'create_engine', create_engine)
        monkeypatch.setattr(ghostdb, 'sessionmaker', sessionmaker)

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

        storage = GhostDBStorage()
        storage.connect(credentials)

        assert storage._session == session
        create_engine.assert_called_once_with(dsn)
        sessionmaker.assert_called_once_with(bind=engine)

    def test_connect_by_dsn(self, monkeypatch):
        engine = Mock()
        session = Mock()
        db = Mock(return_value=session)
        create_engine = Mock(return_value=engine)
        sessionmaker = Mock(return_value=db)

        monkeypatch.setattr(ghostdb, 'create_engine', create_engine)
        monkeypatch.setattr(ghostdb, 'sessionmaker', sessionmaker)

        dsn = 'gdb://test:test@local:321/kpi'

        storage = GhostDBStorage()
        storage.connect({'dsn': dsn})

        assert storage._session == session
        create_engine.assert_called_once_with(dsn)
        sessionmaker.assert_called_once_with(bind=engine)

    def test_store(self):
        session = Mock()
        obj = Mock()

        storage = GhostDBStorage()
        storage._session = session

        storage.store(obj)

        session.add.assert_called_once_with(obj)
        session.commit.assert_called_once()
