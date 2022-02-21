# -*- coding: utf-8 -*-
from mocon.model import BaseModel


def test_model_meta_default():
    class User(BaseModel):
        name: str
        age: int

    assert User.Meta.global_key_prefix == ""
    assert User.Meta.model_key_prefix == "tests.test_model:user"
    assert User.Meta.encoding == "utf-8"
    assert not User.Meta.embedded
    assert User.Meta.db_key

    user = User(name="John Doe", age=42)
    assert user.key.startswith("tests.test_model:user:")


def test_model_meta_no_defined_default():
    class User(BaseModel):
        class Meta:
            db_key = "test"
            embedded = True
            encoding = "utf-16"

        name: str
        age: int

    assert User.Meta.global_key_prefix == ""
    assert User.Meta.model_key_prefix == "tests.test_model:user"
    assert User.Meta.encoding == "utf-16"
    assert User.Meta.embedded
    assert User.Meta.db_key == "test"

    user = User(name="test", age=10)
    assert user.key == "tests.test_model:user:test"


def test_model_meta_inherited():
    class User(BaseModel):
        class Meta:
            model_key_prefix = "test"
            encoding = "utf-8"

        name: str
        age: int

    class Admin(User):
        pass

    assert Admin.Meta.global_key_prefix == ""
    assert Admin.Meta.model_key_prefix == "tests.test_model:admin"
    assert Admin.Meta.encoding == "utf-8"
