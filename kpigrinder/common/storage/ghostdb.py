import typing

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class GhostDBStorage:

    def connect(self, options):
        if options.get('dsn'):
            dsn = options['dsn']
        else:
            dsn = '{dbtype}://{login}:{password}@{host}:{port}/{schema}'.format(
                dbtype=options['conn_type'],
                login=options['login'],
                password=options['password'],
                host=options['host'],
                port=options['port'],
                schema=options['schema']
            )

        engine = create_engine(dsn)
        db = sessionmaker(bind=engine)

        self._session = db()

    def store(self, obj: typing.Any):
        self._session.add(obj)
        self._session.commit()
