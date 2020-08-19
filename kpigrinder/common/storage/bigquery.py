import typing
import sentry_sdk
from google.cloud import bigquery

from .formatter import BigQueryFormatter


class BigQueryStoreException(Exception):
    ...


class BigQueryStorage:

    def connect(self, options):
        self._client = bigquery.Client()
        self._table = self._client.get_table(options['table_name'])

    def store(self, obj: typing.Any):
        errors = self._client.insert_rows_json(
            self._table,
            [
                BigQueryFormatter.format(obj),
            ]
        )

        for error in errors:
            sentry_sdk.capture_exception(
                BigQueryStoreException(
                    'Unable to store row into BigQuery: {}'.format(
                        error
                    )
                )
            )
