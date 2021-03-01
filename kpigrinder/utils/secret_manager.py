import json
from functools import lru_cache
from google.api_core.exceptions import NotFound
from google.cloud import secretmanager_v1beta1 as secretmanager

from kpigrinder import config
from .singleton import Singleton


class SecretManager(metaclass=Singleton):

    def __init__(self):
        self._project_id = config.GCP_PROJECT_ID
        self._cli = secretmanager.SecretManagerServiceClient()

    @lru_cache(maxsize=16)
    def get_secret(self, name: str, version: str = 'latest') -> dict:
        name = '{}{}'.format(config.SECRET_MANAGER_NAME_PREFIX, name)
        version = self._cli.access_secret_version(
            request={'name': self.secret_version_path(self._project_id, name, version)}
        )

        return json.loads(version.payload.data)

    @staticmethod
    def secret_version_path(project, secret, version):
        return 'projects/{project}/secrets/{secret}/versions/{version}'.format(
            project=project,
            secret=secret,
            version=version
        )
