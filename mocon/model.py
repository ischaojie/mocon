# -*- coding: utf-8 -*-
import json
import uuid
from typing import Any, ClassVar, Optional, TypeVar

from pydantic import BaseModel as PydanticBaseModel, ValidationError
from pydantic.main import ModelMetaclass

from mocon.sources import Source
from mocon.exceptions import NoSourceError

T = TypeVar("T", bound="BaseModel")


class BaseMeta:
    # data source
    source: Source = None

    # the model encoding format when saving to the store
    encoding: str = "utf-8"

    # Model prefix for get or save in the store
    # Default value will be the module name concat model name
    global_key_prefix: Optional[str] = None
    model_key_prefix: Optional[str] = None

    # the primary key of the model
    db_key: Optional[str] = None

    # is support embedded model
    embedded: bool = False

    # model control
    can_view: bool = True
    can_edit: bool = True
    can_delete: bool = True


def _set_meta_default(cls, meta, base_meta):
    if not getattr(meta, "encoding", None):
        meta.encoding = getattr(base_meta, "encoding", "utf-8")

    if not getattr(meta, "global_key_prefix", None):
        meta.global_key_prefix = getattr(base_meta, "global_key_prefix", "")

    if not getattr(meta, "model_key_prefix", None):
        meta.model_key_prefix = f"{cls.__module__}:{cls.__name__}".lower()

    if not getattr(meta, "db_key", None):
        meta.db_key = getattr(base_meta, "db_key", uuid.uuid4().hex)

    if not getattr(meta, "embedded", None):
        meta.embedded = getattr(base_meta, "embedded", False)

    if not getattr(meta, "source", None):
        meta.source = getattr(base_meta, "source", None)


class BaseModelMeta(ModelMetaclass):
    _meta: BaseMeta

    def __new__(mcs, name, bases, attrs, **kwargs):
        cls = super().__new__(mcs, name, bases, attrs, **kwargs)
        meta = attrs.get("Meta", None)

        # if cls not defined Meta, get from parent
        meta = meta or getattr(cls, "Meta", None)
        base_meta = getattr(cls, "_meta", None)
        # no inherited, defined Meta
        if meta and meta != BaseMeta and meta != base_meta:
            cls.Meta = meta
            cls._meta = meta
        # inherited Meta
        elif base_meta:
            cls._meta = type(
                f"{cls.__name__}Meta", (base_meta,), dict(base_meta.__dict__)
            )
            cls.Meta = cls._meta
            # remove inherited meta attr
            cls._meta.model_key_prefix = None
        # no defined Meta, no inherited, use default
        else:
            cls._meta = type(
                f"{cls.__name__}Meta", (BaseMeta,), dict(BaseMeta.__dict__)
            )
            cls.Meta = cls._meta

        # set Meta default value if there is no defined
        _set_meta_default(cls, cls._meta, base_meta)

        return cls


class BaseModel(PydanticBaseModel, metaclass=BaseModelMeta):
    """
    Example:

    class UserModel(BaseModel):
        class Meta:
            can_edit = False

        name: str
        age: int

    user = UserModel(name="John", age=18)
    user.save()

    """

    Meta = BaseMeta
    identity: ClassVar[str]

    def __init__(__pydantic_self__, **data: Any) -> None:
        super().__init__(**data)
        __pydantic_self__.validate_source()

    @property
    def key(self):
        db_key = getattr(self._meta, "db_key")
        global_prefix = getattr(self._meta, "global_key_prefix", "")
        model_prefix = getattr(self._meta, "model_key_prefix", "")
        return f"{global_prefix}:{model_prefix}:{db_key}".strip(":")

    @classmethod
    def validate_source(cls):
        if cls._meta.source is None or not isinstance(cls._meta.source, Source):
            raise NoSourceError("Model must have a Source client")

    @classmethod
    def get(cls, key: str) -> Optional["BaseModel"]:
        data = cls._meta.source.get(key)
        if not data:
            return None
        return cls.parse_raw(data, encoding=cls._meta.encoding)

    def save(self) -> bool:
        return self._meta.source.set(self.key, self.json())

    def delete(self) -> bool:
        return self._meta.source.delete(self.key)

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
