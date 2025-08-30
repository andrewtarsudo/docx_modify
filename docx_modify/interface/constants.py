# -*- coding: utf-8 -*-
from enum import Enum
from typing import NamedTuple, Any

from PySide6.QtCore import QRect, QSize
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QBoxLayout
from loguru import logger


class DirectionLayout(Enum):
    H = "horizontal"
    V = "vertical"
    NA = "not_assigned"

    def __missing__(self, key):
        logger.error(f"Направление {key} не определено, поэтому проигнорировано")
        return self.__class__.NA

    def layout(self):
        _layout_dict: dict[str, Any] = {
            "horizontal": QHBoxLayout(),
            "vertical": QVBoxLayout()}

        return _layout_dict.get(self._value_, QBoxLayout(QBoxLayout.Direction.LeftToRight))

    def __repr__(self):
        return f"<{self.__class__.__name__}({self._name_})>"

    def __str__(self):
        return f"{self.__class__.__name__}: {self._value_}"


class Geometry(NamedTuple):
    left: int
    top: int
    width: int
    height: int

    def to_dict(self) -> dict[str, int]:
        return {attr: getattr(self, attr) for attr in self._fields}

    def to_qrect(self):
        return QRect(self.left, self.top, self.width, self.height)

    def __str__(self):
        _values_str: list[str] = [*self.to_dict()]
        return ", ".join(_values_str)

    def __repr__(self):
        return f"<{self.__class__.__name__}({str(self)})>"

    def size(self):
        return QSize(self.width, self.height)


class InputAttribute(Enum):
    DOCUMENT_MODE = "document_mode"
    DOCUMENT_SIDE = "document_side"
    DEF_MINISTRY = "def_ministry"
    CHANGE_LIST = "change_list"
    APPROVEMENT_LIST = "approvement_list"

    def __repr__(self):
        return f"<{self.__class__.__name__}({self._name_})>"

    def __str__(self):
        return f"{self.__class__.__name__}: {self._value_}"


class WidgetAttrs(NamedTuple):
    name: str
    geometry: Geometry
    font: QFont
    text: str | None
    attr: InputAttribute | None = None
    value: Any = None

    def check_not_none(self, attr: str):
        return getattr(self, attr) is not None

    def to_tuple(self) -> tuple[Any, ...]:
        return tuple(filter(self.check_not_none, self._fields))

    def __str__(self):
        _values_str: list[str] = [*self.to_tuple()]
        return ", ".join(_values_str)

    def __repr__(self):
        return f"<{self.__class__.__name__}({str(self)})>"
