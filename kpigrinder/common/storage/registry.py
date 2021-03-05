import time
import orjson
from hashlib import sha224
from sqlalchemy.orm import session

from kpigrinder.config import STORAGE_REGISTRY_TTL
from kpigrinder.utils.singleton import Singleton


def json_ext_serialize(obj):
    if isinstance(obj, session.Session):
        return id(obj)
    raise TypeError('unable to serialize type {}'.format(type(obj)))


class StorageRegistry(metaclass=Singleton):

    def __init__(self):
        self._storages = {
            # [ttl, storage instance],
        }

    def get_storage(self, klass, options: dict):
        key = '{src_path}:{class_name}-{params}'.format(
            src_path=klass.__module__,
            class_name=klass.__name__,
            params=sha224(orjson.dumps(options, default=json_ext_serialize)).hexdigest(),
        )

        ttl, instance = self._storages.get(key, [0, None])
        if instance is None or time.time() > ttl:
            instance = klass()
            instance.connect(options)
            self._storages[key] = [None, instance]

        self._storages[key][0] = time.time() + STORAGE_REGISTRY_TTL

        return instance

    def clean(self):
        tm = time.time()
        rotten_keys = []
        for key, (ttl, _) in self._storages.items():
            if tm > ttl:
                rotten_keys.append(key)

        for key in rotten_keys:
            del self._storages[key]
