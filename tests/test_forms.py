# -*- coding: utf-8 -*-
from wsgiref.validate import validator
from mocon.forms import Converter, model_to_form, SUPPORTED_CONVERTERS
from mocon.model import BaseModel
from wtforms.form import Form
from wtforms.fields import StringField, IntegerField
from wtforms import validators
import pytest
from mocon import Field


class User(BaseModel):
    name: str
    age: int



def test_converter_handle_str():
    class My(BaseModel):
        name: str = Field(
            default="chaojie",
            description="user name",
            title="UserName",
            min_length=2,
            max_length=12,
        )

    str_field = Converter().convert(My.__fields__["name"])
    assert str_field.field_class == StringField
    assert str_field.name == "UserName"
    assert str_field.kwargs["description"] == "user name"
    assert str_field.kwargs["default"] == "chaojie"
    validator_cls = [v.__class__ for v in str_field.kwargs["validators"]]
    assert validators.Optional in validator_cls
    assert validators.Length in validator_cls


def test_converter_handle_int():
    class MyInt(BaseModel):
        age: int

    pass


def test_model_to_form_fields_exist():
    UserForm = model_to_form(User)
    assert UserForm.__name__ == "UserForm"
    assert issubclass(UserForm, Form)


def test_model_to_form_converter():
    pass
