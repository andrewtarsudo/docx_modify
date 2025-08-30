# -*- coding: utf-8 -*-
from typing import Type

from loguru import logger
from lxml.etree import ElementBase

from docx_modify.core_elements.clark_name import fqdn
from docx_modify.enum_element import DocumentMode, SectionOrientation, SectionPgBorder, SectionPgMar, SectionPgSz, \
    DocumentSide
from docx_modify.exceptions import InvalidOrientationError
from docx_modify.xml_elements.xml_document import XmlDocument
from docx_modify.xml_elements.xml_element_factory import new_xml
from docx_modify.xml_elements.xml_file import XmlFilePart
from docx_modify.xml_elements.xml_hdr_ftr import HdrFtrReference


class XmlSection(XmlFilePart):
    def __init__(
            self,
            xml_document: XmlDocument,
            section_index: int,
            document_mode: DocumentMode,
            document_side: DocumentSide):
        tag: str = "w:sectPr"
        super().__init__(tag, xml_document, section_index)
        self._xml_document: XmlDocument = xml_document
        self._section_index: int = self._idx
        self._document_mode: DocumentMode = document_mode
        self._document_side: DocumentSide = document_side

    def _set_pg_num_type(self):
        raise NotImplementedError

    def _set_pg_sz(self):
        _conversion_table: dict[SectionOrientation, SectionPgSz] = {
            SectionOrientation.PORTRAIT: SectionPgSz.a4_portrait(),
            SectionOrientation.LANDSCAPE: SectionPgSz.a4_landscape()
        }
        element: ElementBase = _conversion_table[self.orientation].element

        self.delete_child_if_exists("w:pgSz")
        self.add_child(element)

        logger.info(f"Секция {self._section_index}, <w:pgSz> добавлен")

    @property
    def orientation(self) -> SectionOrientation:
        orient: str | None = self.get_child("w:pgSz").get(fqdn("w:orient"), None)

        if orient is None or orient == "portrait":
            return SectionOrientation.PORTRAIT

        elif orient == "landscape":
            return SectionOrientation.LANDSCAPE

        else:
            logger.error(f"Некорректная ориентация секции {orient}, Секция {self._section_index}")
            raise InvalidOrientationError

    def _set_pg_borders(self):
        raise NotImplementedError

    def _set_title_pg(self):
        if self._section_index in (0, 1):
            self.add_child_if_not_exists("w:titlePg")
            logger.info(f"Секция {self._section_index}, <w:titlePg> добавлен")

        else:
            self.delete_child_if_exists("w:titlePg")
            logger.info(f"Секция {self._section_index}, <w:titlePg> удален")

    def set_section(self):
        self._set_pg_sz()
        self._set_pg_mar()
        self._set_title_pg()
        self._set_pg_borders()
        self._set_pg_num_type()
        self._delete_header_footer_references()

        logger.info(f"Секция {self._section_index} задана")

    def _delete_header_footer_references(self):
        _header_references = self.get_descendants("w:headerReference")
        _footer_references = self.get_descendants("w:footerReference")
        self.delete_children([*_header_references, *_footer_references])

    def add_header_footer_reference(self, hdr_ftr_reference: HdrFtrReference):
        _attrs: dict[str, str] = {
            str(fqdn("r:id")): f"{hdr_ftr_reference.rid}",
            str(fqdn("w:type")): hdr_ftr_reference.ref_type.value}

        element: ElementBase = new_xml(hdr_ftr_reference.reference.value, attributes=_attrs)
        self.add_child(element, 0)

        logger.info(
            f"Секция {self._section_index}, Reference {hdr_ftr_reference.rid} {hdr_ftr_reference.reference} "
            f"Reference Type {hdr_ftr_reference.ref_type.value} добавлена в документ")

    def _set_pg_mar(self):
        raise NotImplementedError

    def make_xml_section_mode(self):
        _dict: dict[DocumentMode, Type[XmlSection]] = {
            DocumentMode.ARCH: XmlSectionArch,
            DocumentMode.TYPO: XmlSectionTypo,
            DocumentMode.PROG: XmlSectionProg}

        cls: Type[XmlSection] = _dict.get(self._document_mode)

        return cls(
            self._xml_document,
            self._section_index,
            self._document_mode,
            self._document_side)


class XmlSectionTypo(XmlSection):
    _pg_mar_section: dict[int, SectionPgMar] = {
        -1: SectionPgMar.typo_landscape_section(),
        0: SectionPgMar.typo_zero_section(),
        1: SectionPgMar.typo_one_section()}

    @property
    def _pg_border_space(self):
        return

    def _set_pg_mar(self):
        if self.orientation == SectionOrientation.LANDSCAPE:
            pg_mar: SectionPgMar = self._pg_mar_section.get(-1)

        elif self._section_index not in self._pg_mar_section:
            pg_mar: SectionPgMar = self._pg_mar_section.get(1)

        else:
            pg_mar: SectionPgMar = self._pg_mar_section.get(self._section_index)

        self.delete_child_if_exists("w:pgMar")
        self.add_child(pg_mar.element)

        logger.info(f"Секция {self._section_index}, <w:pgMar> задан")

    def _set_pg_borders(self):
        self.delete_child_if_exists("w:pgBorders")
        logger.info("<w:pgBorders> удален")

    def _set_pg_num_type(self):
        self.delete_child_if_exists("w:pgNumType")


class XmlSectionArch(XmlSection):
    _pg_border_space_portrait: dict[str, int] = {
        "top": 0,
        "bottom": 0,
        "left": 14,
        "right": 14}

    _pg_border_space_landscape: dict[str, int] = {
        "top": 21,
        "bottom": 0,
        "left": 21,
        "right": 19}

    _pg_mar_section: dict[int, SectionPgMar] = {
        -1: SectionPgMar.arch_landscape_section(),
        0: SectionPgMar.arch_zero_section(),
        1: SectionPgMar.arch_one_section(),
        2: SectionPgMar.arch_two_section()}

    def _get_pg_border(self, side: SectionPgBorder | str):
        if isinstance(side, SectionPgBorder):
            side: str = side.value

        _attrs: dict[str, str] = {
            "w:color": "auto",
            "w:space": f"{self._pg_border_space.get(side)}",
            "w:sz": "12",
            "w:val": "single"}

        return new_xml(f"w:{side}", attributes=_attrs)

    @property
    def _pg_border_space(self) -> dict[str, int]:
        if self.orientation == SectionOrientation.PORTRAIT:
            return self._pg_border_space_portrait

        elif self.orientation == SectionOrientation.LANDSCAPE:
            return self._pg_border_space_landscape

        else:
            logger.error(f"Некорректная ориентация секции {self.orientation}")
            raise InvalidOrientationError

    def _set_pg_mar(self):
        if self.orientation == SectionOrientation.LANDSCAPE:
            pg_mar: SectionPgMar = self._pg_mar_section.get(-1)

        elif self._section_index not in self._pg_mar_section:
            pg_mar: SectionPgMar = self._pg_mar_section.get(2)

        else:
            pg_mar: SectionPgMar = self._pg_mar_section.get(self._section_index)

        self.delete_child_if_exists("w:pgMar")
        self.add_child(pg_mar.element)
        logger.info(f"Секция {self._section_index}, <w:pgMar> задан")
        return

    def _set_pg_borders(self):
        self.delete_child_if_exists("w:pgBorders")

        children: list[ElementBase] = [self._get_pg_border(side) for side in self._pg_border_space]
        attributes: dict[str, str] = {"w:offsetFrom": "text"}
        _pg_borders: ElementBase = new_xml("w:pgBorders", children=children, attributes=attributes)
        self.add_child(_pg_borders)

        logger.info(f"Секция {self._section_index}, рамка добавлена в документ")

    def _set_pg_num_type(self):
        self.delete_child_if_exists("w:pgNumType")

        if self._document_side == DocumentSide.SINGLE or self._section_index != 1:
            return

        else:
            attributes: dict[str, str] = {"w:start": "3"}
            pg_num_type: ElementBase = new_xml("w:pgNumType", attributes=attributes)
            self.add_child(pg_num_type)

            logger.info(f"Секция {self._section_index}, нумерация страниц, начиная с 3, задана")


class XmlSectionProg(XmlSection):
    _pg_border_space_portrait: dict[str, int] = {
        "top": 0,
        "bottom": 0,
        "left": 14,
        "right": 14}

    _pg_border_space_landscape: dict[str, int] = {
        "top": 21,
        "bottom": 0,
        "left": 21,
        "right": 19}

    _pg_mar_section: dict[int, SectionPgMar] = {
        -1: SectionPgMar.prog_landscape_section(),
        0: SectionPgMar.prog_zero_section(),
        1: SectionPgMar.prog_one_section(),
        2: SectionPgMar.prog_one_section()}

    def _get_pg_border(self, side: SectionPgBorder | str):
        if isinstance(side, SectionPgBorder):
            side: str = side.value

        _attrs: dict[str, str] = {
            "w:color": "auto",
            "w:space": f"{self._pg_border_space.get(side)}",
            "w:sz": "12",
            "w:val": "single"}

        return new_xml(f"w:{side}", attributes=_attrs)

    @property
    def _pg_border_space(self) -> dict[str, int]:
        if self.orientation == SectionOrientation.PORTRAIT:
            return self._pg_border_space_portrait

        elif self.orientation == SectionOrientation.LANDSCAPE:
            return self._pg_border_space_landscape

        else:
            logger.error(f"Некорректная ориентация секции {self.orientation}")
            raise InvalidOrientationError

    def _set_pg_mar(self):
        if self.orientation == SectionOrientation.LANDSCAPE:
            pg_mar: SectionPgMar = self._pg_mar_section.get(-1)

        elif self._section_index not in self._pg_mar_section:
            pg_mar: SectionPgMar = self._pg_mar_section.get(1)

        else:
            pg_mar: SectionPgMar = self._pg_mar_section.get(self._section_index)

        self.delete_child_if_exists("w:pgMar")
        self.add_child(pg_mar.element)
        logger.info(f"Секция {self._section_index}, <w:pgMar> добавлен")

    def _set_pg_borders(self):
        self.delete_child_if_exists("w:pgBorders")
        logger.info("<w:pgBorders> удален")

    def _set_pg_num_type(self):
        self.delete_child_if_exists("w:pgNumType")

        if self._document_side == DocumentSide.SINGLE:
            return

        if self._section_index != 1:
            return

        attributes: dict[str, str] = {"w:start": "3"}
        pg_num_type: ElementBase = new_xml("w:pgNumType", attributes=attributes)
        self.add_child(pg_num_type)

        logger.info(f"Секция {self._section_index}, нумерация страниц, начиная с 3, задана")
