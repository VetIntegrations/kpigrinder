import typing


class GhostDBStorage:

    def connect(self, options):
        self._session = options['db']

    def store(self, obj: typing.Any):
        self._session.add(obj)
        self._session.commit()
