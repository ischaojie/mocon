# -*- coding: utf-8 -*-
from tkinter import S

import pytest
from mocon.model import BaseModel
from mocon.sources import Source
from mocon.exceptions import NoSourceError


class Movie(BaseModel):
    class Meta:
        source = Source("redis://localhost:6379/0")
        model_key_prefix = "movie"
        encoding = "utf-8"

    title: str
    year: int
    director: str


def test_model_meta_default():
    class User(BaseModel):
        name: str
        age: int

        class Meta:
            source = Source("redis://localhost:6379/0")

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
            source = Source("redis://localhost:6379/0")
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
            source = Source("redis://localhost:6379/0")
            model_key_prefix = "test"
            encoding = "utf-8"

        name: str
        age: int

    class Admin(User):
        pass

    assert Admin.Meta.global_key_prefix == ""
    assert Admin.Meta.model_key_prefix == "tests.test_model:admin"
    assert Admin.Meta.encoding == "utf-8"


def test_model_key_model_key_prefix():
    movie = Movie(title="The Matrix", year=1999, director="Lana Wachowski")
    assert movie.key.startswith("movie:")


def test_model_key_global_key_prefix():
    class Te(BaseModel):
        class Meta:
            source = Source("redis://localhost:6379/0")
            global_key_prefix = "test"
            model_key_prefix = "te"

        title: str

    t = Te(title="The Matrix")
    assert t.key.startswith("test:te:")


def test_model_meta_source():
    class User(BaseModel):
        name: str

    with pytest.raises(NoSourceError):
        User(name="test")


def test_model_base():
    movie = Movie(title="Harry Potter", year=2001, director="Chris Columbus")
    movie.save()
    movie_db = Movie.get(movie.key)
    assert movie_db.title == "Harry Potter"
    assert movie_db.year == 2001
    assert movie_db.director == "Chris Columbus"
    movie.delete()
    assert not Movie.get(movie.key)
