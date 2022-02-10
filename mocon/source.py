# -*- coding: utf-8 -*-
import json
from io import IOBase
from json import JSONDecodeError
from typing import Any


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
