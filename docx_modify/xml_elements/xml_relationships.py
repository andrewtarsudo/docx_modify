# -*- coding: utf-8 -*-
from typing import Iterable, Any, NamedTuple

from loguru import logger
from lxml.etree import ElementBase

from docx_modify.core_elements.core_zip_file import CoreZipFile
from docx_modify.enum_element import XmlRelationshipTarget, XmlRelationshipType
from docx_modify.xml_elements.xml_element_factory import new_xml
from docx_modify.xml_elements.xml_file import XmlFile


class XmlRelationshipsFile(XmlFile):
    def __init__(self, name: str, core_zip_file: CoreZipFile):
        super().__init__(name, core_zip_file)
        self._xml_relationships: dict[str, 'XmlRelationship'] = {}

    def __getitem__(self, item):
        if isinstance(item, str):
            return self._xml_relationships.get(item)

        elif isinstance(item, int):
            return self._xml_relationships.get(f"rId{item}")

        else:
            logger.error(f"Идентификатор {item} должен быть типа str или int, но получено {type(item)}")
            return

    def __setitem__(self, key, value):
        if not isinstance(key, (int, str)) or not isinstance(value, XmlRelationship):
            logger.error(
                f"Ключ {key} должен быть типа str или int, а значение {value} -- типа XmlRelationship, "
                f"но получено {type(key)} и {type(value)}")
            return

        if isinstance(key, int):
            key: str = f"rId{key}"

        self._xml_relationships[key] = value

    def __contains__(self, item):
        if isinstance(item, str):
            return item in self._xml_relationships.keys()

        elif isinstance(item, int):
            return f"rId{item}" in self._xml_relationships.keys()

        elif isinstance(item, XmlRelationship):
            return item in self._xml_relationships.values()

        else:
            return False

    def __len__(self):
        return len(self._xml_relationships)

    def items(self):
        return self._xml_relationships.items()

    def set_xml_relationships(self):
        for child in iter(self):
            rel_id: str = child.get("Id")
            rel_type: XmlRelationshipType = XmlRelationshipType(child.get("Type"))
            rel_target: str = child.get("Target")
            self[rel_id] = XmlRelationship(rel_id, rel_type, rel_target, self)

    def __add__(self, other):
        if isinstance(other, XmlRelationship):
            xml_relationship: XmlRelationship = other

        elif isinstance(other, tuple) and len(other) == 2:
            rel_type, rel_target = other

            if not isinstance(rel_type, XmlRelationshipType) or not isinstance(rel_target, XmlRelationshipTarget):
                logger.error(
                    f"Элементы добавляемого Relationship {other} имеют не те типы:\n"
                    f"{type(rel_type)}, {type(rel_target)}")
                return NotImplemented

            else:
                xml_relationship: XmlRelationship = self.generate_xml_relationship(rel_type, rel_target)

        else:
            return NotImplemented

        self[xml_relationship.rel_id] = xml_relationship
        rel: ElementBase = new_xml("Relationship", attributes=xml_relationship.attrs)
        self.add_child(rel)
        logger.info(f"Relationship {xml_relationship.rel_id}, Target {xml_relationship.rel_target} добавлено")

    __radd__ = __add__
    __iadd__ = __add__

    def __delitem__(self, key):
        element: ElementBase = self.find_child("Id", key)

        if element is not None:
            self.delete_child(element)
            del self._xml_relationships[key]
            logger.info(f"XmlRelationship rId{key} удалено")

        else:
            logger.info(f"XmlRelationship rId{key} не найдено")

        return

    def next_rel_id(self) -> int:
        _rel_ids: tuple[int, ...] = tuple(map(lambda x: int(f"{x[3:]}"), self._xml_relationships.keys()))
        return max(_rel_ids) + 1

    def generate_xml_relationship(
            self,
            rel_type: XmlRelationshipType,
            rel_target: XmlRelationshipTarget | str) -> 'XmlRelationship':
        rel_id: str = f"rId{self.next_rel_id()}"

        return XmlRelationship(rel_id, rel_type, rel_target, self)

    def delete_rels(self, rels: Iterable[str | int | Any] = None):
        if rels is None:
            rels: list[str] = [*self._xml_relationships.keys()]

        for xml_relationship in rels:
            if isinstance(xml_relationship, str):
                item: str = xml_relationship

            elif isinstance(xml_relationship, int):
                item: str = f"rId{xml_relationship}"

            elif isinstance(xml_relationship, XmlRelationship):
                item: str = xml_relationship.rel_id

            else:
                logger.error("Невозможный вариант, случилась серьезная ошибка")
                logger.error(f"xml_relationship: {xml_relationship}, тип {type(xml_relationship)}")
                continue

            del self[item]
            logger.info(f"Relationship {item} удалено")

        self.write()

    def add_xml_relationship(self, xml_relationship: 'XmlRelationship'):
        _attrs: dict[str, str] = {
            "Id": f"rId{xml_relationship.rel_id}",
            "Type": xml_relationship.rel_type.value,
            "Target": xml_relationship.rel_target}

        element: ElementBase = new_xml("Relationship", attributes=_attrs)
        self.add_child(element)
        self._xml_relationships[f"rId{xml_relationship.rel_id}"] = xml_relationship
        logger.info(f"Relationship rId{xml_relationship.rel_id} добавлено в документ")

    def hdr_ftr_references(self) -> dict[str, str]:
        return {
            v.rel_target: k for k, v in self._xml_relationships.items()
            if v.rel_type in (XmlRelationshipType.HEADER, XmlRelationshipType.FOOTER)}


class XmlRelationship(NamedTuple):
    rel_id: str
    rel_type: XmlRelationshipType
    target: XmlRelationshipTarget | str
    parent: XmlRelationshipsFile

    @property
    def rel_target(self):
        if isinstance(self.target, XmlRelationshipTarget):
            return self.target.value

        else:
            return self.target

    def __str__(self):
        return f"{self.__class__.__name__}: {self.rel_id}, {str(self.rel_type)}, {self.rel_target}"

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.rel_id}, {repr(self.rel_type)}, {self.rel_target})>"

    def __hash__(self):
        return hash(self.rel_id)

    @property
    def rid(self) -> int:
        return int(self.rel_id[3:])

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.rid == other.rid

        else:
            return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return self.rid != other.rid

        else:
            return NotImplemented

    def __gt__(self, other):
        if isinstance(other, self.__class__):
            return self.rid > other.rid

        else:
            return NotImplemented

    def __ge__(self, other):
        if isinstance(other, self.__class__):
            return self.rid >= other.rid

        else:
            return NotImplemented

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return self.rid < other.rid

        else:
            return NotImplemented

    def __le__(self, other):
        if isinstance(other, self.__class__):
            return self.rid <= other.rid

        else:
            return NotImplemented

    def __bool__(self):
        return True

    @property
    def attrs(self):
        return {
            "Id": self.rel_id,
            "Type": self.rel_type,
            "Target": self.rel_target}


class XmlWordRelationships(XmlRelationshipsFile):
    def __init__(self, core_zip_file: CoreZipFile):
        name: str = "word/_rels/document.xml.rels"
        super().__init__(name, core_zip_file)


class XmlRelationshipsGlobal(XmlRelationshipsFile):
    def __init__(self, core_zip_file: CoreZipFile):
        name: str = "_rels/.rels"
        super().__init__(name, core_zip_file)

    def add_custom(self):
        self.set_xml_relationships()

        rel_type: XmlRelationshipType = XmlRelationshipType.CUSTOM_PROPERTIES
        rel_target: str = "docProps/custom.xml"
        xml_relationship: XmlRelationship = self.generate_xml_relationship(rel_type, rel_target)

        self.add_xml_relationship(xml_relationship)

        logger.info(
            f"В файл {self._name} было добавлено XmlRelationship {xml_relationship.rid} "
            f"для {xml_relationship.target}")
