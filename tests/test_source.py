# -*- coding: utf-8 -*-
import io

from mocon.store import Source


def test_source_with_file():
    file = io.StringIO("{'a': 1}")
    source = Source(file)
    assert source.get()
