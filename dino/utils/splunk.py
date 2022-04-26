from contextlib import contextmanager

import splunklib.client as client
import ujson
from splunklib.binding import HTTPError


class SplunkHEC:
    def __init__(self, index: str, host: str, username: str, password: str):
        service = client.connect(
            host=host, username=username, password=password, autologin=True
        )
        try:
            service.indexes.get(index)
        except HTTPError:
            service.indexes.create(index)
        self._index = service.indexes[index]

    @contextmanager
    def stream(self, sourcetype: str, host: str, source: str):
        self._sock = self._index.attach(sourcetype=sourcetype, host=host, source=source)
        try:
            yield self
        finally:
            if self._sock:
                self._sock.close()

    def send(self, data: bytes):
        self._sock.send(data)

    def send_dict(self, data: dict, **kwargs):
        self.send(ujson.dumps(data, **kwargs).encode("utf-8") + b"\n")
