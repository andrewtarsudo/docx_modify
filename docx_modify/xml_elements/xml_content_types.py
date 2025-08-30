# -*- coding: utf-8 -*-
from loguru import logger
from lxml.etree import ElementBase

from docx_modify.const import HeaderFooter
from docx_modify.core_elements.core_zip_file import CoreZipFile
from docx_modify.enum_element import DocumentMode
from docx_modify.xml_elements.xml_element_factory import new_xml_no_ns
from docx_modify.xml_elements.xml_file import XmlFile

_CONTENT_TYPES: tuple[str, str] = ("footer+xml", "header+xml")


def generate_hdr_ftr(hdr_ftr: HeaderFooter | str, max_value: int = 0):
    content_type: str = f"application/vnd.openxmlformats-officedocument.wordprocessingml.{hdr_ftr}+xml"

    _children: set[ElementBase] = set()

    for index in range(1, max_value + 1):
        attributes: dict[str, str] = {
            "PartName": f"/word/{hdr_ftr}{index}.xml",
            "ContentType": content_type}
        child: ElementBase = new_xml_no_ns("Override", attributes=attributes)
        _children.add(child)

    return _children


class XmlContentTypes(XmlFile):
    _document_mode_nums: dict[DocumentMode, dict[HeaderFooter | str, int]] = {
        DocumentMode.ARCH: {
            "header": 4,
            "footer": 7},
        DocumentMode.TYPO: {
            "header": 4,
            "footer": 4},
        DocumentMode.PROG: {
            "header": 4,
            "footer": 4}}

    def __init__(self, core_zip_file: CoreZipFile, document_mode: DocumentMode):
        name: str = "[Content_Types].xml"
        super().__init__(name, core_zip_file)
        self._document_mode: DocumentMode = document_mode

    def _add_png(self):
        child: ElementBase = self.find_child("Extension", "png")

        if child is None:
            attributes: dict[str, str] = {
                "Extension": "png",
                "ContentType": "image/png"}
            child: ElementBase = new_xml_no_ns("Default", attributes=attributes)
            self.add_child(child)
            logger.info("Extension png добавлено")

        else:
            logger.info("Extension png обнаружено в списке")

    def _delete_override_headers_footers(self):
        children: list[ElementBase] = [
            child for child in self.get_descendants("{*}Override")
            if child.get("ContentType").endswith(_CONTENT_TYPES)]
        partnames: str = "\n".join(sorted(map(lambda x: x.get("PartName"), children)))
        self.delete_children(children)
        logger.info(f"Удалены части, PartName:\n{partnames}")

    def _add_override_headers_footers(self):
        _headers: set[ElementBase] = generate_hdr_ftr(
            "header", self._document_mode_nums.get(self._document_mode).get("header"))
        _footers: set[ElementBase] = generate_hdr_ftr(
            "footer", self._document_mode_nums.get(self._document_mode).get("footer"))
        _hdr_ftr: list[ElementBase] = [*_headers, *_footers]
        self.add_children(_hdr_ftr)

        _hdr_ftr_items: str = "\n".join(sorted(map(lambda x: x.get("PartName"), _hdr_ftr)))
        logger.info(f"Добавлены части, PartNames:\n{_hdr_ftr_items}")

    def fix_content_types(self):
        self.read()
        self._add_png()
        self._delete_override_headers_footers()
        self._add_override_headers_footers()
        self.write()
