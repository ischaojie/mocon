# -*- coding: utf-8 -*-
from mocon.models import BaseModel


def test_base_model_create():
    class TestModel(BaseModel):
        title: str
