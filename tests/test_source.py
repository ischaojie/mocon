# -*- coding: utf-8 -*-
import pytest

from mocon.sources import SourceURL


@pytest.mark.parametrize(
    "url, dialect",
    [
        ("redis://localhost:6379/0", "redis"),
        ("mongodb://localhost:27017/", "mongodb"),
        ("memcached://localhost:11211/", "memcached"),
    ],
)
def test_source_url(url, dialect):
    url = SourceURL(url)
    assert url.dialect == dialect
