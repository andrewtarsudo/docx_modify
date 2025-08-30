# -*- coding: utf-8 -*-
from pathlib import Path

from loguru import logger
from lxml import etree

from docx_modify.core_elements.core_zip_file import CoreZipFile
from docx_modify.xml_elements.xml_file import XmlFile


class XmlDocument(XmlFile):
    def __init__(self, core_zip_file: CoreZipFile):
        name: str = "word/document.xml"
        super().__init__(name, core_zip_file)

    def __len__(self):
        return len(self.get_descendants("w:sectPr"))

    def _path_to_save(self) -> Path:
        return self._core_zip_file.path_dir.joinpath(self._name)

    def save(self):
        super().save()
        logger.info(f"Документ сохранен в {self._path_to_save()}")

    def read(self, **kwargs):
        self._etree = etree.parse(self.full_path)
        self._content = self._etree.getroot()
