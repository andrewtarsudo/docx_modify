# -*- coding: utf-8 -*-
from pathlib import Path
from typing import Iterable, Iterator

from loguru import logger
from lxml import etree
# noinspection PyProtectedMember
from lxml.etree import ElementBase, _ElementTree

from docx_modify.const import parent_path
from docx_modify.core_elements.clark_name import fqdn
from docx_modify.core_elements.core_zip_file import CoreZipFile
from docx_modify.xml_elements.xml_file import XmlFile


class XmlStyles(XmlFile):
    def __init__(self, core_zip_file: CoreZipFile, basic_file: Path, styles: Iterable[str] = None):
        if styles is None:
            styles: list[str] = []

        name: str = "word/styles.xml"
        super().__init__(name, core_zip_file)
        self._basic_file: Path = basic_file
        self._styles: tuple[str, ...] = *styles,

    def iter_styles(self) -> Iterator[str]:
        return iter(self._styles)

    def add_styles(self):
        self.read()
        _styles_id: tuple[str, ...] = tuple(child.get(fqdn("w:styleId")) for child in iter(self))
        logger.info(f"{self.__class__.__name__}._styles_id = \n{_styles_id}")

        for style in self.iter_styles():
            if style in _styles_id:
                _style_xml: ElementBase | None = self.find_child("w:styleId", style)
                self.delete_child(_style_xml)
                logger.info(f"Стиль {style} удален")

        _et: _ElementTree = etree.parse(self._basic_file)
        _root: ElementBase = _et.getroot()

        for file_style in tuple(_root):
            self.add_child(file_style)
            logger.info(f"Стиль {file_style.get(fqdn('w:styleId'))} добавлен")

        self.write()
        logger.info("XML-стили обновлены")
        return


class XmlBasicStyles(XmlStyles):
    def __init__(self, core_zip_file: CoreZipFile):
        basic_file: Path = parent_path.joinpath("sources/styles/styles.xml")
        styles: tuple[str, ...] = (
            "_style_table_11_",
            "_style_table_11_left_",
            "_style_12_center_",
            "_style_12_table_footer_",
            "_style_text_14_",
            "_style_text_14_left_",
            "_style_text_16_",
            "_table_style_new_grid_")
        super().__init__(core_zip_file, basic_file, styles)


class XmlChangeListStyles(XmlStyles):
    def __init__(self, core_zip_file: CoreZipFile):
        basic_file: Path = parent_path.joinpath("sources/change_list_styles/styles.xml")
        styles: tuple[str, ...] = (
            "_table_style_change_list_",
            "_change_list_text_",
            "_change_list_header_")
        super().__init__(core_zip_file, basic_file, styles)
