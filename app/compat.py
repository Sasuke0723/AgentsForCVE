"""计划功能：提供最小兼容层，在缺少第三方依赖时仍可使用接近 Pydantic 的建模接口。"""

from __future__ import annotations

import copy
import json
from typing import Any


_MISSING = object()


class FieldInfo:
    """保存字段默认值与描述信息。"""

    def __init__(
        self,
        default: Any = _MISSING,
        *,
        default_factory: Any = None,
        description: str | None = None,
    ) -> None:
        self.default = default
        self.default_factory = default_factory
        self.description = description


def Field(
    default: Any = _MISSING,
    *,
    default_factory: Any = None,
    description: str | None = None,
) -> FieldInfo:
    """提供与 Pydantic 相近的字段声明形式。"""

    return FieldInfo(default, default_factory=default_factory, description=description)


class BaseModel:
    """只实现当前项目所需的最小 BaseModel 能力。"""

    def __init__(self, **data: Any) -> None:
        fields = self._collect_fields()

        for name in fields:
            if name in data:
                value = data.pop(name)
            else:
                value = self._default_value_for(name)
            setattr(self, name, value)

        for name, value in data.items():
            setattr(self, name, value)

    @classmethod
    def _collect_fields(cls) -> dict[str, Any]:
        fields: dict[str, Any] = {}
        for base in reversed(cls.__mro__):
            annotations = getattr(base, "__annotations__", {})
            fields.update(annotations)
        return fields

    @classmethod
    def _default_value_for(cls, name: str) -> Any:
        if hasattr(cls, name):
            raw_default = getattr(cls, name)
            if isinstance(raw_default, FieldInfo):
                if raw_default.default_factory is not None:
                    return raw_default.default_factory()
                if raw_default.default is Ellipsis or raw_default.default is _MISSING:
                    raise TypeError(f"Missing required field: {name}")
                return copy.deepcopy(raw_default.default)
            return copy.deepcopy(raw_default)
        raise TypeError(f"Missing required field: {name}")

    def model_dump(self) -> dict[str, Any]:
        return {
            name: self._dump_value(getattr(self, name))
            for name in self._collect_fields()
            if hasattr(self, name)
        }

    def model_dump_json(self, indent: int | None = None) -> str:
        return json.dumps(self.model_dump(), ensure_ascii=False, indent=indent)

    @classmethod
    def model_validate(cls, data: dict[str, Any]) -> "BaseModel":
        return cls(**data)

    @staticmethod
    def _dump_value(value: Any) -> Any:
        if isinstance(value, BaseModel):
            return value.model_dump()
        if isinstance(value, list):
            return [BaseModel._dump_value(item) for item in value]
        if isinstance(value, dict):
            return {key: BaseModel._dump_value(item) for key, item in value.items()}
        return value

    def __repr__(self) -> str:
        field_parts = ", ".join(
            f"{name}={getattr(self, name)!r}"
            for name in self._collect_fields()
            if hasattr(self, name)
        )
        return f"{self.__class__.__name__}({field_parts})"
