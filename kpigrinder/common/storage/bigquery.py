import logging
import typing
import sentry_sdk
from google.cloud import bigquery

from .formatter import BigQueryFormatter


logger = logging.getLogger(__name__)


class BigQueryStoreException(Exception):
    ...


class BigQueryStorage:

    def connect(self, options):
        self._client = bigquery.Client()
        self._table = self._client.get_table(options['table_name'])

    def get_connection(self):
        return self._client

    def store(self, obj: typing.Any):
        errors = self._client.insert_rows_json(
            self._table,
            [
                BigQueryFormatter.format(obj),
            ]
        )

        for error in errors:
            logger.error('Unable to store row into BigQuery: {}'.format(error))

            sentry_sdk.capture_exception(
                BigQueryStoreException(
                    'Unable to store row into BigQuery: {}'.format(
                        error
                    )
                )
            )
