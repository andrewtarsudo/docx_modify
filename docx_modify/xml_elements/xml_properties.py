# -*- coding: utf-8 -*-
from re import Pattern, compile, RegexFlag, match
from typing import NamedTuple

from loguru import logger
from lxml.etree import ElementBase

from docx_modify.const import parent_path
from docx_modify.core_elements.clark_name import fqdn
from docx_modify.core_elements.core_zip_file import CoreZipFile
from docx_modify.enum_element import DocumentSide, CompanyName
from docx_modify.exceptions import InvalidXmlElementError
from docx_modify.xml_elements.xml_element_factory import new_xml_no_ns, new_xml
from docx_modify.xml_elements.xml_file import XmlFile
from docx_modify.xml_elements.xml_object import XmlObject


class DocProperty(NamedTuple):
    fmtid: str
    pid: int
    name: str
    lpwstr: str

    def __str__(self):
        return (
            f"{self.__class__.__name__}:\n"
            f"fmtid = {self.fmtid}, "
            f"pid = {self.pid}, "
            f"name = {self.name}, "
            f"lpwstr = {self.lpwstr}")

    def __repr__(self):
        return (
            f"{self.__class__.__name__}:\n"
            f"<DocProperty pid=\"{self.pid}\" name=\"{self.name}\">\n"
            f"  <vt:lpwstr>{self.lpwstr}</vt:lpwstr>\n"
            f"</DocProperty>")

    def __hash__(self):
        return hash(tuple(getattr(self, attr) for attr in self._fields))

    @classmethod
    def from_xml(cls, element: ElementBase):
        attributes: tuple[str, ...] = ("fmtid", "pid", "name")

        if any(fqdn(attr) not in element.keys() for attr in attributes):
            _attr_str: str = ", ".join(attributes)
            logger.error(f"У элемента Property отсутствует хотя бы один из обязательных атрибутов: {_attr_str}")
            raise InvalidXmlElementError

        fmtid: str = element.get("fmtid")
        pid: int = int(element.get("pid"))
        name: str = element.get("name")
        lpwstr: str = element[0].text

        return cls(fmtid, pid, name, lpwstr)

    def element(self):
        child: ElementBase = new_xml("vt:lpwstr")
        child.text = self.lpwstr
        attributes: dict[str, str] = {
            "fmtid": self.fmtid,
            "pid": f"{self.pid}",
            "name": self.name
        }
        element: ElementBase = new_xml_no_ns("property", attributes=attributes)
        element.append(child)
        return element


class XmlProperties(XmlFile):
    patterns: dict[str, Pattern] = {
        "_DocName_": compile(r"(?=.*doc|.*project)(?=.*name).*", RegexFlag.IGNORECASE),
        "_DocType_": compile(r"(?=.*doc)(?=.*type)(?!.*short).*", RegexFlag.IGNORECASE),
        "_DecimalNum_": compile(r"(?=.*dec)(?=.*num).*", RegexFlag.IGNORECASE),
        "_DocTypeShort_": compile(r"(?=.*doc)(?=.*type)(?=.*short).*", RegexFlag.IGNORECASE)
    }

    def __init__(self, core_zip_file: CoreZipFile, document_side: DocumentSide):
        name: str = "docProps/custom.xml"

        with open(parent_path.joinpath("sources/default/custom.xml").resolve(), "rb") as fb:
            default: bytes = fb.read()

        super().__init__(name, core_zip_file, default)
        self._document_side: DocumentSide = document_side
        self._doc_properties: list[DocProperty] = []
        self._max_pid: int = -1

    def __str__(self):
        _str_properties: str = "\n".join(str(_property) for _property in self._doc_properties)
        return f"{self.__class__.__name__}:\n{_str_properties}\n"

    __repr__ = __str__

    def __len__(self):
        return len(self._doc_properties)

    def __contains__(self, item):
        if isinstance(item, DocProperty):
            return item in self._doc_properties

        elif isinstance(item, str):
            return item in self.property_names

        else:
            return False

    def __getitem__(self, item):
        if isinstance(item, (int, slice)):
            return self._doc_properties[item]

        elif isinstance(item, str):
            for doc_property in self._doc_properties:
                if doc_property.name == item:
                    return doc_property

            else:
                logger.info(f"Некорректный ключ {item}")
                return

        else:
            return NotImplemented

    def __add__(self, other):
        if isinstance(other, DocProperty):
            self._doc_properties.append(other)

        elif other is not None:
            logger.info(
                f"Добавляемый элемент {str(other)} должен быть типа DocProperty или None, "
                f"но получено {type(other)}")

    def _find_properties(self):
        for k, v in self.patterns.items():
            for doc_property in self._doc_properties:
                name: str = doc_property.name

                if match(v, name) and name != k:
                    self._duplicate_property(name, k)
                    break

            else:
                logger.warning(f"DocProperty {k} не найдено в документе")

    def set_properties(self, company_name: CompanyName):
        doc_properties: list[DocProperty] = [DocProperty.from_xml(child) for child in iter(self)]

        for doc_property in doc_properties:
            self + doc_property

        self._max_pid = len(self) + 1
        self._find_properties()
        self._add_page_sheet_property()
        self._add_company_name_property(company_name)
        self.save()

    @property
    def property_names(self) -> set[str]:
        return set(child.get(fqdn("name")) for child in iter(self))

    def _add_property(self, name: str, lpwstr: str):
        fmtid: str = "{D5CDD505-2E9C-101B-9397-08002B2CF9AE}"
        pid: int = self._max_pid + 1
        doc_property: DocProperty = DocProperty(fmtid, pid, name, lpwstr)
        self.add_child(doc_property.element())

        self._max_pid += 1

        logger.info(f"DocProperty {name} и значением {lpwstr} добавлено")

    def _duplicate_property(self, name_from: str, name_to: str):
        if name_from not in self.property_names:
            logger.info(f"DocProperty {name_from} не найдено")

        elif name_to in self.property_names:
            logger.info(f"DocProperty {name_to} уже задано")

        else:
            doc_property: DocProperty = self[name_from]
            name: str = name_to
            lpwstr: str = doc_property.lpwstr
            self._add_property(name, lpwstr)

    def _add_page_sheet_property(self):
        name: str = "_Page_Sheet_"

        if self._document_side == DocumentSide.SINGLE:
            lpwstr: str = "Лист"

        else:
            lpwstr: str = "Стр."

        self._add_property(name, lpwstr)

    def _add_company_name_property(self, company_name: CompanyName):
        name: str = "_Company_Name_"
        lpwstr: str = company_name.full_name()

        self._add_property(name, lpwstr)

    def get_property(self, property_name: str):
        xml_object: XmlObject = XmlObject(self._content)
        child: ElementBase | None = xml_object.find_child("name", property_name)

        if child is None:
            logger.error(
                f"В документе не найдено свойство {property_name}, "
                f"поэтому используется логотип ПРОТЕЙ СТ по умолчанию")
            return None

        else:
            return DocProperty.from_xml(child)
