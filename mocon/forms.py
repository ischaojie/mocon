# -*- coding: utf-8 -*-

from typing import Any, Callable, Dict, Sequence, Union, no_type_check

from pydantic import BaseModel
from pydantic.fields import ModelField
from wtforms import Form, StringField, validators, Field


@no_type_check
def convert(*args: str):
    def inner(func: Callable) -> Callable:
        func._converter_for = frozenset(args)
        return func

    return inner


class BaseConverter:
    def __init__(self) -> None:
        # conv_mapping for each BaseModel type_ mapping to a converter
        # for example: type `str` mapping to wtforms StringField
        conv_mapping = {}
        for method in dir(self):
            obj = getattr(self, method)
            if hasattr(obj, "_converter_for"):
                for arg in obj._converter_for:
                    conv_mapping[arg] = obj
        self.converters = conv_mapping

    def convert(self, field: ModelField):
        # https://wtforms.readthedocs.io/en/3.0.x/fields/#wtforms.fields.Field.__init__

        field_info = field.field_info

        field_args = {
            "validators": [],
            "filters": [],
            "description": field_info.description,
            "default": field_info.default,
            "name": field_info.title,
        }
        # add validators
        if field.required:
            field_args["validators"].append(validators.InputRequired())
        else:
            field_args["validators"].append(validators.Optional())

        # TODO: validator length (min=- 1, max=- 1, message=None)

        converter = self.converters.get(field.type_.__name__)
        if not converter:
            pass
        return converter(**field_args)


class Converter(BaseConverter):
    @convert("str")
    def conv_str(self, field_args: Dict, **kwargs: Any) -> Field:
        """convert str type to StringField"""
        return StringField(**field_args)


def model_to_form(
    model: BaseModel,
    only: Sequence[str] = None,
    exclude: Sequence[str] = None,
):
    """Model convert to Form"""
    conveter = Converter()
    form_fields = {}

    for name, model_field in model.__fields__.items():
        if only and name not in only:
            continue
        if exclude and name in exclude:
            continue
        form_field = conveter.convert(model, model_field)
        if form_field:
            form_fields[name] = form_field

    return type(f"{model.__name__}Form", (Form,), form_fields)
