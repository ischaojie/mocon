# -*- coding: utf-8 -*-
import pydantic
from typing import Type, Any, Optional

from mocon.exceptions import InvalidKeyException
from mocon.models import BaseModel

Field = pydantic.Field


class ModelField:
    def __init__(
        self,
        pydantic_field: pydantic.fields.ModelField,
        model_cls: Type["BaseModel"] = None,
        parent: Optional["ModelField"] = None,
    ):
        self._model_cls = model_cls
        self._pydantic_field = pydantic_field
        self._parent = parent

    def __getattr__(self, attr) -> Any:
        assert self._model_cls is not None
        if attr not in self._model_cls.__mocon_fields__:
            raise InvalidKeyException(
                f"Model '{self._model_cls.__name__}' has no attribute '{attr}'"
            )
        child_field: ModelField = self._model_cls.__mocon_fields__[attr]
        return ModelField(
            pydantic_field=child_field._pydantic_field,
            model_cls=child_field._model_cls,
            parent=self,
        )
