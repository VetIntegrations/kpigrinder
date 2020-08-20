from unittest.mock import Mock

from kpigrinder.common.storage import bigquery
from kpigrinder.common.storage.bigquery import BigQueryStorage, BigQueryStoreException, BigQueryFormatter


class TestBigQueryStorage:

    def test_connect(self, monkeypatch):
        TABLE_NAME = 'test-bq-table'

        table = Mock()
        client = Mock(**{'get_table.return_value': table})
        bigquery_client = Mock(return_value=client)
        monkeypatch.setattr(bigquery.bigquery, 'Client', bigquery_client)

        storage = BigQueryStorage()
        storage.connect({'table_name': TABLE_NAME})

        assert storage._client == client
        assert storage._table == table
        bigquery_client.assert_called_once()
        client.get_table.assert_called_once_with(TABLE_NAME)

    def test_store(self, monkeypatch):
        client = Mock(**{'insert_rows_json.return_value': []})

        monkeypatch.setattr(BigQueryFormatter, 'format', lambda obj: obj)

        storage = BigQueryStorage()
        storage._client = client
        storage._table = Mock()

        obj = Mock()
        storage.store(obj)

        client.insert_rows_json.assert_called_once_with(storage._table, [obj])

    def test_store_handling_error(self, monkeypatch):
        error = 'ERR0R_ID'
        sentry = Mock()
        client = Mock(**{'insert_rows_json.return_value': [error]})

        monkeypatch.setattr(BigQueryFormatter, 'format', lambda obj: obj)
        monkeypatch.setattr(bigquery, 'sentry_sdk', sentry)

        storage = BigQueryStorage()
        storage._client = client
        storage._table = Mock()

        obj = Mock()
        storage.store(obj)

        client.insert_rows_json.assert_called_once_with(storage._table, [obj])
        sentry.capture_exception.assert_called_once()
        assert isinstance(sentry.capture_exception.mock_calls[0][1][0], BigQueryStoreException)
        sentry.capture_exception.mock_calls[0][1][0].args[0] == 'Unable to store row into BigQuery: {}'.format(error)
