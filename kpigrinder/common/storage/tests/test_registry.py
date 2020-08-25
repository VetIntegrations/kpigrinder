import time
import pytest
from hashlib import sha1
from unittest.mock import Mock

from kpigrinder import config
from kpigrinder.common.storage.registry import StorageRegistry


class TestStorageRegistry:

    @pytest.fixture(autouse=True)
    def setup(self):
        yield

        # Erase storages in SotrageRegostry as last is singleton
        registry = StorageRegistry()
        registry._storages = {}

    def test_get_storage_empty_case(self):
        storage = Mock()
        storage_class = Mock(__name__='TestStorage', return_value=storage, )
        registry = StorageRegistry()

        assert registry._storages == {}

        assert registry.get_storage(storage_class, {}) == storage

        storage_class.assert_called_once()
        storage.connect.assert_called_once_with({})

    def test_get_storage_old_ttl_case(self):
        storage = Mock()
        storage_class = Mock(__name__='TestStorage', return_value=storage, )
        registry = StorageRegistry()
        key = '{src_path}:{class_name}-{params}'.format(
            src_path=storage_class.__module__,
            class_name=storage_class.__name__,
            params=sha1(b'{}').hexdigest(),
        )
        registry._storages == {
            key: [time.time() - config.STORAGE_REGISTRY_TTL - 1, storage]
        }

        assert registry._storages == {}

        assert registry.get_storage(storage_class, {}) == storage

        storage_class.assert_called_once()
        storage.connect.assert_called_once_with({})

    def test_get_storage_take_existing_case(self):
        storage = Mock()
        storage_class = Mock(__name__='TestStorage', return_value=storage, )
        registry = StorageRegistry()
        key = '{src_path}:{class_name}-{params}'.format(
            src_path=storage_class.__module__,
            class_name=storage_class.__name__,
            params=sha1(b'{}').hexdigest(),
        )
        registry._storages == {
            key: [time.time(), storage]
        }

        assert registry.get_storage(storage_class, {}) == storage

        storage_class.assert_not_called
        storage.connect.assert_not_called

    def test_clean(self):
        registry = StorageRegistry()
        registry._storages = {
            '0': [time.time() + config.STORAGE_REGISTRY_TTL, 1],
            '1': [time.time() - 1, 1],
        }

        registry.clean()
        assert list(registry._storages.keys()) == ['0']
