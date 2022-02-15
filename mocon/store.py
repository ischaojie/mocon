# -*- coding: utf-8 -*-
from collections.abc import Sequence
from typing import Any, Optional, Mapping


class StoreBackend:
    def connect(self) -> None:
        raise NotImplementedError()

    def disconnect(self) -> None:
        raise NotImplementedError()

    def connection(self) -> "ConnectionBackend":
        raise NotImplementedError()


class ConnectionBackend:
    def acquire(self) -> None:
        raise NotImplementedError()

    def release(self) -> None:
        raise NotImplementedError()

    def get(self) -> Optional["Record"]:
        raise NotImplementedError()


class Record(Sequence):
    @property
    def _mapping(self) -> Mapping:
        raise NotImplementedError()  # pragma: no cover


class Source:
    """
    file = open("/home/mocon/test.txt", "r")
    source = Source(file)
    """

    def __init__(self, client, **kwargs):
        assert hasattr(client, "get") and hasattr(
            client, "set"
        ), "Client must have get and set methods"
        self.client = client

    def get(self, name) -> Any:
        return self.client.get(name)

    def set(self, name, value) -> bool:
        return self.client.set(name, value)
