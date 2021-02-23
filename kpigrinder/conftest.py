import pytest

from kpigrinder import celery


pytest_plugins = (
    'ghostdb.conftest',
)


@pytest.fixture(autouse=True)
def celery_setup(dbsession, monkeypatch):
    monkeypatch.setattr(celery.CeleryBaseTask, '_db', dbsession)
