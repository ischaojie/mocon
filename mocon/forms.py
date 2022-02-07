# -*- coding: utf-8 -*-
from typing import ClassVar, Type, Dict
import pydantic
from mocon.exceptions import InvalidModelException
from mocon.models import BaseModel
from mocon.source import Source


class BaseMeta(pydantic.BaseConfig):
    source = Source
    name: ClassVar[str] = ""
    can_edit: ClassVar[bool] = True
    can_delete: ClassVar[bool] = True


class BaseFormMeta(pydantic.main.ModelMetaclass):

    def __new__(mcs, name, bases, namespace, **kwargs):
        __mocon_fields__: Dict[str, ]
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)

        model = kwargs.get("model")
        if not model:
            return cls

        # check model is subclass of BaseModel
        if not issubclass(model, BaseModel):
            raise InvalidModelException("Class {model.__name__} is not a pydantic model")

        cls.model = model
        cls.identity = model.__name__
        cls.name = namespace.get("name", cls.model.__name__)

        return cls


class BaseForm(metaclass=BaseFormMeta):
    """Base form"""

    Meta = ClassVar[BaseMeta]

    # pydantic model
    model: ClassVar[type]

    identity: ClassVar[str]
