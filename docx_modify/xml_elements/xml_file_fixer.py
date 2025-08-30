# -*- coding: utf-8 -*-
from pathlib import Path

from loguru import logger
from lxml import etree
# noinspection PyProtectedMember
from lxml.etree import ElementBase, _ElementTree

from docx_modify.const import _MIRROR_ARCH_FORMULA, _SINGLE_ARCH_FORMULA, temp_path, parent_path
from docx_modify.enum_element import DocumentMode, DocumentSide
from docx_modify.exceptions import InvalidXmlFileError, InvalidOptionError
from docx_modify.xml_elements.xml_object import XmlObject


class XmlFileFixer:
    _folder: Path = temp_path.joinpath("_docx_temp").joinpath("word")

    def __init__(
            self, *,
            document_mode: DocumentMode,
            document_side: DocumentSide,
            approvement_list: bool):
        self._xml_file_name: str | None = None
        self._xml_object: XmlObject | None = None
        self._document_mode: DocumentMode = document_mode
        self._document_side: DocumentSide = document_side
        self._approvement_list: bool = approvement_list

    def __repr__(self):
        return f"<{self.__class__.__name__}({self._xml_file_name}, {repr(self._xml_object)})>"

    def __str__(self):
        return f"{self._xml_file_name}, {str(self._xml_object)}"

    def __bool__(self):
        return self._xml_file_name is not None

    def __hash__(self):
        return hash(self._xml_file_name)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._xml_file_name == other._xml_file_name

        else:
            return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return self._xml_file_name != other._xml_file_name

        else:
            return NotImplemented

    @property
    def full_xml_file_path(self):
        return self._folder.joinpath(self._xml_file_name)

    def _clear(self):
        self._xml_file_name = None
        self._xml_object = None

    def _set_file(self, name: str):
        path: Path = self._folder.joinpath(name)

        if not path.exists():
            logger.error(f"Файл {path} не найден")
            raise InvalidXmlFileError

        elif path.suffix != ".xml":
            logger.error(f"Некорректный файл {path} для обработки как XML-файла")
            raise InvalidXmlFileError

        self._xml_file_name: str = name

    def _read(self):
        self._xml_object = XmlObject.read(self.full_xml_file_path)

    def _write(self):
        self._xml_object.write(self.full_xml_file_path)

    def _replace_formula(self):
        tag: str = "w:insertFormula"

        if self._document_mode == DocumentMode.TYPO or self._document_mode == DocumentMode.PROG:
            return

        if self._document_side == DocumentSide.MIRROR:
            element: ElementBase = etree.fromstring(_MIRROR_ARCH_FORMULA)
            logger.success("Формула для подсчета страниц добавлена")

        elif self._document_side == DocumentSide.SINGLE:
            element: ElementBase = etree.fromstring(_SINGLE_ARCH_FORMULA)
            logger.success("Формула для подсчета листов добавлена")

        else:
            logger.error(f"Некорректное значение вида печати: {self._document_side}")
            raise InvalidOptionError

        self._xml_object.replace(tag, element)

    def _replace_paragraph(self):
        if self._document_mode == DocumentMode.TYPO:
            return

        elif self._approvement_list:
            xml: _ElementTree = etree.parse(parent_path.joinpath("sources/default/approvement_list.xml"))
            root: ElementBase = xml.getroot()

            for child in root.iterchildren():
                self._xml_object.add_child(child)

            logger.success("Информация про Лист утверждения добавлена")

    def replace(self):
        self._set_file("footer3.xml")
        self._read()
        self._replace_formula()
        self._write()
        self._clear()
        self._set_file("header1.xml")
        self._read()
        self._replace_paragraph()
        self._write()
        self._clear()
