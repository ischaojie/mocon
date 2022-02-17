# -*- coding: utf-8 -*-
from mocon.model import BaseModel


def test_model_meta_default():
    class User(BaseModel):
        name: str
        age: int

    # assert User.meta.db_key.startswith("tests.test_model:user")
    assert User.meta.global_key_prefix == ""
    assert User.meta.model_key_prefix == "tests.test_model:user"
    assert User.meta.encoding == "utf-8"
    assert User.meta.embedded == False


def test_model_meta_no_defined_default():
    class User(BaseModel):
        class Meta:
            db_key = "test"

        name: str
        age: int

    assert User.meta.model_key_prefix == "tests.test_model:user"
    assert User.meta.encoding == "utf-8"
    # assert User.meta.embedded == False
    user = User(name="test", age=10)
    assert user.key() == "tests.test_model:user:test"


def test_model_meta_inherited():
    class User(BaseModel):
        class Meta:
            model_key_prefix = "test"
            encoding = "utf-8"

        name: str
        age: int

    class Admin(User):
        pass

    assert Admin.meta.model_key_prefix == "test"
    assert Admin.meta.encoding == "utf-8"
