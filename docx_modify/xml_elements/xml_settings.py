# -*- coding: utf-8 -*-
from loguru import logger
from lxml.etree import ElementBase

from docx_modify.core_elements.clark_name import fqdn
from docx_modify.core_elements.core_zip_file import CoreZipFile
from docx_modify.enum_element import DocumentSide, DocumentMode
from docx_modify.xml_elements.xml_element_factory import new_xml
from docx_modify.xml_elements.xml_file import XmlFile


class XmlSettings(XmlFile):
    def __init__(self, core_zip_file: CoreZipFile, side: DocumentSide, document_mode: DocumentMode):
        name: str = "word/settings.xml"
        super().__init__(name, core_zip_file)
        self._document_side: DocumentSide = side
        self._document_mode: DocumentMode = document_mode

    def _set_mirror_margins(self):
        mirror_margins: ElementBase = self.get_or_add_child("w:mirrorMargins")

        if self._document_side == DocumentSide.MIRROR:
            mirror_margins.set(fqdn("w:val"), "1")
            logger.info("Зеркальные отступы заданы")

        elif self._document_side == DocumentSide.SINGLE:
            mirror_margins.set(fqdn("w:val"), "0")
            logger.info("Зеркальные отступы удалены")

    def _set_borders_do_not_surround(self):
        self.delete_child_if_exists("w:bordersDoNotSurroundHeader")
        self.delete_child_if_exists("w:bordersDoNotSurroundFooter")
        borders_do_not_surround_header: ElementBase = new_xml("w:bordersDoNotSurroundHeader")
        borders_do_not_surround_footer: ElementBase = new_xml("w:bordersDoNotSurroundFooter")

        if self._document_mode == DocumentMode.ARCH:
            borders_do_not_surround_header.set(fqdn("w:val"), "0")
            borders_do_not_surround_footer.set(fqdn("w:val"), "0")
            logger.info("Колонтитулы заключены в рамку")

        elif self._document_mode == DocumentMode.TYPO or self._document_mode == DocumentMode.PROG:
            borders_do_not_surround_header.set(fqdn("w:val"), "1")
            borders_do_not_surround_footer.set(fqdn("w:val"), "1")
            logger.info("Колонтитулы не заключены в рамку")

    def _set_even_and_odd_headers(self):
        even_and_odd_headers: ElementBase = self.get_or_add_child("w:evenAndOddHeaders")

        if self._document_side == DocumentSide.MIRROR:
            even_and_odd_headers.set(fqdn("w:val"), "1")
            logger.info("Колонтитулы для четных и нечетных страниц заданы")

        elif self._document_side == DocumentSide.SINGLE:
            even_and_odd_headers.set(fqdn("w:val"), "0")
            logger.info("Колонтитулы для четных и нечетных страниц заданы")

    def _set_parameter(self, child: str, tag: str | None = None, value: str | None = None):
        self.delete_child_if_exists(child)

        if tag is not None:
            attributes: dict[str, str] = {tag: f"{value}"}
            logger.info(f"Элемент {child}, <{tag}> = {value}")

        else:
            attributes: dict[str, str] = {}
            logger.info(f"Элемент {child} добавлен")

        _param: ElementBase = new_xml(child, attributes=attributes)
        self.add_child(_param)

    def set_settings(self):
        self.read()
        self._set_mirror_margins()
        self._set_even_and_odd_headers()
        self._set_borders_do_not_surround()

        self._set_parameter("w:alignBordersAndEdges")
        logger.info("Выравнивание границ и краев заданы")

        self.write()
