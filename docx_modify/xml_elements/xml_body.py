# -*- coding: utf-8 -*-
from pathlib import Path

from lxml import etree
# noinspection PyProtectedMember
from lxml.etree import ElementBase, _ElementTree

from docx_modify.const import parent_path
from docx_modify.xml_elements.xml_document import XmlDocument
from docx_modify.xml_elements.xml_element_factory import new_xml
from docx_modify.xml_elements.xml_file import XmlFilePart


class XmlBody(XmlFilePart):
    def __init__(self, xml_document: XmlDocument):
        super().__init__("w:body", xml_document)

    def _add_page_break(self):
        attributes: dict[str, str] = {"w:type": "page"}
        br: ElementBase = new_xml("w:br", attributes=attributes)
        r: ElementBase = new_xml("w:r")
        r.append(br)
        p: ElementBase = new_xml("w:p")
        p.append(r)
        self.add_before_last_child(p, "w:sectPr")

    def _add_list_change_header(self):
        attributes: dict[str, str] = {"w:val": "_change_list_header_"}
        p_style: ElementBase = new_xml("w:pStyle", attributes=attributes)

        p_pr: ElementBase = new_xml("w:pPr")
        p_pr.append(p_style)

        t: ElementBase = new_xml("w:t")
        t.text = "Лист регистрации изменений"

        r: ElementBase = new_xml("w:r")
        r.append(t)

        p: ElementBase = new_xml("w:p")
        p.append(p_pr)
        p.append(r)
        self.add_before_last_child(p, "w:sectPr")

    def _add_list_change(self):
        _xml_file: Path = parent_path.joinpath("sources/change_list/change_list_table.xml")
        _element_tree: _ElementTree = etree.parse(_xml_file)

        element: ElementBase
        for element in _element_tree.getroot().iterchildren():
            self.add_before_last_child(element, "w:sectPr")

    def set_change_list(self):
        self.read()
        self._add_page_break()
        self._add_list_change_header()
        self._add_list_change()
        self.write()
