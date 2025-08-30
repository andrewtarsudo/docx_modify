# -*- coding: utf-8 -*-
from pathlib import Path
from typing import Iterable, Iterator

from loguru import logger
from lxml import etree
# noinspection PyProtectedMember
from lxml.etree import ElementBase, _ElementTree

from docx_modify.core_elements.clark_name import fqdn
from docx_modify.xml_elements.xml_element_factory import new_xml


class XmlObject:
    DOCTYPE: str = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'

    def __init__(self, content: ElementBase | None = None):
        self._content: ElementBase | None = content

    def __str__(self):
        return f"<{self._content.tag}/>"

    def __repr__(self):
        return repr(self._content)

    def __iter__(self) -> Iterator[ElementBase]:
        return self._content.iterchildren()

    def __contains__(self, item):
        if isinstance(item, ElementBase):
            return item in iter(self)

        elif isinstance(item, str):
            return self.get_child(item) is not None

        else:
            return False

    def get_child(self, tag: str) -> ElementBase | None:
        return self._content.find(fqdn(tag))

    def get_descendants(self, tag: str) -> list[ElementBase]:
        return list(self._content.iterdescendants(fqdn(tag)))

    def add_child(self, child: ElementBase, pos: int = None):
        if pos is None:
            self._content.append(child)
        else:
            self._content.insert(pos, child)

    def add_children(self, children: Iterable[ElementBase]):
        for child in children:
            self._content.append(child)

    def delete_child(self, child: ElementBase):
        self._content.remove(child)

    def delete_children(self, children: Iterable[ElementBase]):
        for child in children:
            self.delete_child(child)

    def find_child(self, attr: str, value: str) -> ElementBase | None:
        for element in iter(self):
            if element.get(fqdn(attr)) == value:
                return element

        else:
            logger.info(f"Элемент с '<{attr}> = {value}' не найден")
            return None

    def get_or_add_child(self, tag: str):
        _child: ElementBase | None = self.get_child(tag)

        if _child is None:
            _child: ElementBase = new_xml(tag)
            self.add_child(_child)

        return _child

    def delete_child_if_exists(self, tag: str):
        _child: ElementBase | None = self.get_child(tag)

        if _child is not None:
            self.delete_child(_child)

    def add_child_if_not_exists(self, tag: str):
        _child: ElementBase | None = self.get_child(tag)

        if _child is None:
            _child: ElementBase = new_xml(tag)
            self.add_child(_child)

    def iter_child_tag(self, tag: str) -> Iterator[ElementBase]:
        return self._content.iterchildren(fqdn(tag))

    def find_child_index(self, tag: str, index: int) -> ElementBase | None:
        _children: list[ElementBase] = list(self.iter_child_tag(tag))

        if not list(self.iter_child_tag(tag)):
            return None

        if -len(_children) > index or index > len(_children) - 1:
            index %= len(_children)

        return _children[index]

    def get_last_child(self, tag: str) -> ElementBase:
        return self.find_child_index(tag, -1)

    def add_before_last_child(self, child: ElementBase, tag: str):
        self.get_last_child(tag).addprevious(child)

    def replace(self, tag: str, element: ElementBase):
        current_element: ElementBase = self.get_descendants(tag)[0]
        current_element.getparent().replace(current_element, element)

    @classmethod
    def read(cls, path: Path):
        _etree: _ElementTree = etree.parse(path)
        return cls(_etree.getroot())

    def write(self, path: Path):
        self._content.getroottree().write(path)
        logger.info(f"Файл {path} записан")
