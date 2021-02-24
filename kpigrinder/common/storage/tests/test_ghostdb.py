from unittest.mock import Mock

from kpigrinder.common.storage.ghostdb import GhostDBStorage


class TestGhostDBStorage:

    def test_store(self):
        session = Mock()
        obj = Mock()

        storage = GhostDBStorage()
        storage._session = session

        storage.store(obj)

        session.add.assert_called_once_with(obj)
        session.commit.assert_called_once()
