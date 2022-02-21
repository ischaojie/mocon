# -*- coding: utf-8 -*-

from typing import Any, Callable, Dict, Sequence, Union, no_type_check

from pydantic import BaseModel
from pydantic.fields import ModelField
from wtforms import (
    BooleanField,
    Field,
    Form,
    IntegerField,
    StringField,
    validators,
    DateField,
    DateTimeField,
    EmailField,
    DecimalField,
    URLField,
    PasswordField,
)

SUPPORTED_CONVERTERS = ("str", "int")


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

        self.handlers = conv_mapping

    def convert(self, field: ModelField):
        # https://wtforms.readthedocs.io/en/3.0.x/fields/#wtforms.fields.Field.__init__

        field_info = field.field_info

        field_args = {
            "validators": [],
            "filters": [],
            "description": field_info.description,
            "default": field.default,
            "name": field_info.title,
        }
        # add validators
        if field.required:
            field_args["validators"].append(validators.InputRequired())
        else:
            field_args["validators"].append(validators.Optional())

        converter = self.handlers.get(field.type_.__name__)
        if not converter:
            pass
        return converter(field=field, field_args=field_args)


class Converter(BaseConverter):
    # TODO: should use constr
    # short_str: constr(min_length=2, max_length=10)
    @convert("str", "constr")
    def handle_str(self, field: ModelField, field_args: Dict, **kwargs: Any) -> Field:
        """convert str type to StringField"""
        if field.type_.__name__ == "constr":
            min_length = (
                field.type_.min_length if hasattr(field.type_, "min_length") else -1
            )
            max_length = (
                field.type_.max_length if hasattr(field.type_, "max_length") else -1
            )
            field_args["validators"].append(
                validators.Length(min=min_length, max=max_length)
            )
        return StringField(**field_args)

    @convert("int")
    def handle_int(self, field_args: Dict, **kwargs: Any) -> Field:
        return IntegerField(**field_args)

    @convert("bool")
    def handle_bool(self, field_args: Dict, **kwargs: Any) -> Field:
        return BooleanField(**field_args)

    @convert("float")
    def handle_float(self, field_args: Dict, **kwargs: Any) -> Field:
        return DecimalField(**field_args)

    @convert("datetime")
    def handle_datetime(self, field_args: Dict, **kwargs: Any) -> Field:
        return DateTimeField(**field_args)

    @convert("date")
    def handle_date(self, field_args: Dict, **kwargs: Any) -> Field:
        return DateField(**field_args)

    @convert("EmailStr")
    def handle_email(self, field_args: Dict, **kwargs: Any) -> Field:
        return EmailField(**field_args)

    @convert("HttpUrl")
    def handle_url(self, field_args: Dict, **kwargs: Any) -> Field:
        return URLField(**field_args)

    @convert("SecretStr")
    def handle_password(self, field_args: Dict, **kwargs: Any) -> Field:
        return PasswordField(**field_args)


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
        form_field = conveter.convert(model_field)
        if form_field:
            form_fields[name] = form_field

    return type(f"{model.__name__}Form", (Form,), form_fields)
