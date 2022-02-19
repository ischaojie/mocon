# -*- coding: utf-8 -*-

from pydantic import BaseModel
from wtforms import Form, StringField
from typing import Any, Callable, Dict, Sequence, no_type_check


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
        for name in dir(self):
            obj = getattr(self, name)
            if hasattr(obj, "_converter_for"):
                for arg in obj._converter_for:
                    conv_mapping[arg] = obj
        self.converters = conv_mapping
    
    def switch_converter():
        pass


class Converter(BaseConverter):
    @convert("str")
    def conv_str(self, field_args: Dict, **kwargs: Any):
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
        form_field = conveter.convert(model, model_field.type_)
        if form_field:
            form_fields[name] = form_field

    return type(f"{model.__name__}Form", (Form,), form_fields)
