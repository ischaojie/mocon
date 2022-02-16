# -*- coding: utf-8 -*-
import json
from tkinter import N
from typing import Optional, TypeVar, ClassVar, Dict, no_type_check, Any

import pydantic
from pydantic import BaseConfig
from pydantic import ValidationError

from mocon.fields import ModelField
from mocon.store import Source

T = TypeVar("T", bound="BaseModel")


class BaseMeta(BaseConfig):
    source: Any = None
    name: Optional[str] = None
    # database key
    db_key: Optional[str] = None

    # model control
    can_view: bool = True
    can_edit: bool = True
    can_delete: bool = True


class BaseModelMeta(pydantic.main.ModelMetaclass):
    __mocon_fields__: Dict[str, ModelField]

    @no_type_check
    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace)
        meta = namespace.get("Meta", None)

        mocon_fields: Dict[str, ModelField] = {}
        for field_name, field in cls.__fields__.items():
            new_field = ModelField(pydantic_field=field, model_cls=field.type_)
            mocon_fields[field_name] = new_field

        cls.__mocon_fields__ = mocon_fields

        return cls

    def __getattr__(self, name: str) -> Any:
        if name in self.__mocon_fields__:
            return self.__mocon_fields__[name]
        return super().__getattribute__(name)


class BaseModel(pydantic.BaseModel, metaclass=BaseModelMeta):

    __mocon_fields__: Dict[str, ModelField]

    Meta = BaseMeta
    identity: ClassVar[str]

    @classmethod
    def get_source(cls):
        # choice_source()
        source = cls.Meta.source.get(cls.Meta.name)
        try:
            j_source = json.loads(source, encoding="utf-8")
            fields = cls.parse_obj(j_source)
        except ValidationError as e:
            pass
        else:
            return fields

    def save(self: T) -> T:
        pass
