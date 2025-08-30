# -*- coding: utf-8 -*-
from enum import Enum
from pathlib import Path
from typing import Iterable, Iterator, NamedTuple

from loguru import logger
from lxml.etree import ElementBase

from docx_modify.const import TriState
from docx_modify.core_elements.clark_name import fqdn
from docx_modify.xml_elements.xml_element_factory import new_xml


class CompanyName(Enum):
    PROTEI_RD = "_logo_protei.png"
    PROTEI_ST = "_logo_st.png"

    def __repr__(self):
        return f"<{self.__class__.__name__}({self._name_})>"

    def __str__(self):
        return f"{self.__class__.__name__}: {self._value_}"

    @classmethod
    def from_decimal_number(cls, decimal_number: str | None):
        # noinspection PyInterpreter
        if decimal_number is None:
            logger.warning(
                "Не задан децимальный номер, поэтому используется логотип ПРОТЕЙ СТ по умолчанию")
            return cls.PROTEI_ST

        elif decimal_number.startswith("ПАМР"):
            logger.info(f"Децимальный номер {decimal_number} -> _logo_protei.png")
            return cls.PROTEI_RD

        elif decimal_number.startswith("ПДРА"):
            logger.info(f"Децимальный номер {decimal_number} -> _logo_st.png")
            return cls.PROTEI_ST

        else:
            logger.warning(
                "Не удалось распознать децимальный номер, поэтому используется логотип ПРОТЕЙ СТ по умолчанию")
            return cls.PROTEI_ST

    def full_name(self):
        if self._value_ == "_logo_protei.png":
            return "«Научно-Технический Центр ПРОТЕЙ»"

        elif self._value_ == "_logo_st.png":
            return "«ПРОТЕЙ СпецТехника»"


class SectionOrientation(Enum):
    """Document section orientation

    Available options: PORTRAIT, LANDSCAPE.
    """
    LANDSCAPE = "landscape"
    PORTRAIT = "portrait"

    def __repr__(self):
        return f"<{self.__class__.__name__}({self._name_})>"

    def __str__(self):
        return f"{self.__class__.__name__}: {self._value_}"


class SectionPgBorder(Enum):
    """Document section page border side

    Available options: TOP, BOTTOM, LEFT, RIGHT, INSIDEH, INSIDEV, TL2BR (top-left to bottom-right),
    TR2BL (top-right to bottom-left).
    """
    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"
    INSIDEH = "insideH"
    INSIDEV = "insideV"
    TL2BR = "tl2br"
    TR2BL = "tr2bl"

    def __repr__(self):
        return f"<{self.__class__.__name__}({self._name_})>"

    def __str__(self):
        return f"{self.__class__.__name__}: {self._value_}"


class SectionPgMar(NamedTuple):
    """Document section page margins

    Attributes:
        bottom (int): The distance from the bottom
        footer (int): The distance from the footer
        gutter (int): The distance from the gutter
        header (int): The distance from the header
        left (int): The distance from the left
        right (int): The distance from the right
        top (int): The distance from the top
    """
    bottom: int
    footer: int
    gutter: int
    header: int
    left: int
    right: int
    top: int

    def __str__(self):
        return f"{self.__class__.__name__}: {self._asdict().values()}"

    def __repr__(self):
        return f"<{self.__class__.__name__}({self._asdict().items()})>"

    @classmethod
    def arch_zero_section(cls):
        """Specifies the class instance for the zero section in the document."""
        return cls(284, 397, 0, 397, 1418, 624, 6804)

    @classmethod
    def arch_one_section(cls):
        """Specifies the class instance for the first section in the document."""
        return cls(3261, 397, 0, 397, 1418, 624, 964)

    @classmethod
    def arch_two_section(cls):
        """Specifies the class instance for the second section in the document."""
        return cls(1701, 397, 0, 397, 1418, 624, 992)

    @classmethod
    def arch_landscape_section(cls):
        """Specifies the class instance for sections oriented as LANDSCAPE."""
        return cls(850, 397, 0, 1616, 1644, 709, 624)

    @classmethod
    def typo_zero_section(cls):
        return cls(1418, 340, 0, 907, 1276, 709, 6946)

    @classmethod
    def typo_one_section(cls):
        return cls(1134, 720, 0, 720, 1701, 850, 1134)

    @classmethod
    def typo_landscape_section(cls):
        """Specifies the class instance for sections oriented as LANDSCAPE."""
        return cls(850, 397, 0, 1616, 1644, 709, 624)

    @classmethod
    def prog_zero_section(cls):
        """Specifies the class instance for the zero section in the document."""
        return cls(1531, 397, 0, 624, 1418, 850, 6804)

    @classmethod
    def prog_one_section(cls):
        """Specifies the class instance for the first section in the document."""
        return cls(1644, 284, 0, 454, 1134, 567, 1531)

    @classmethod
    def prog_landscape_section(cls):
        """Specifies the class instance for sections oriented as LANDSCAPE."""
        return cls(850, 397, 0, 1616, 1644, 709, 624)

    @property
    def element(self) -> ElementBase:
        """Specifies the xml element

        Generates the object with all fields as attributes.

        Returns:
             ElementBase: The element to add to the XML file
        """
        element: ElementBase = new_xml("w:pgMar")
        for field in self._fields:
            element.set(fqdn(f"w:{field}"), f"{getattr(self, field)}")

        return element


class SectionPgSz(NamedTuple):
    """Document section page size

   Attributes:
       h (int): The page height
       w (int): The page width
       orient (str): The page orientation, portrait or landscape
   """
    h: int
    w: int
    orient: str

    def __str__(self):
        return f"{self.__class__.__name__}: {self._asdict().values()}"

    def __repr__(self):
        return f"<{self.__class__.__name__}({self._asdict().items()})>"

    @classmethod
    def a4_portrait(cls):
        """Specifies the class instance for sections oriented as PORTRAIT."""
        return cls(16_838, 11_906, "portrait")

    @classmethod
    def a4_landscape(cls):
        """Specifies the class instance for sections oriented as LANDSCAPE."""
        return cls(11_906, 16_838, "landscape")

    @property
    def element(self) -> ElementBase:
        """Specifies the xml element

        Generates the object with all fields as attributes.

        Returns:
            ElementBase: The object to add to the XML file.
            Does not add the 'w:orient' attribute if the value is 'portrait'.
        """
        element: ElementBase = new_xml("w:pgSz")
        for field in self._fields:
            if field == "orient" and self.orient == "portrait":
                continue
            else:
                element.set(fqdn(f"w:{field}"), f"{getattr(self, field)}")
        return element


class XmlRelationshipTarget(Enum):
    """Document relationship target

    Aliases: footer1 - footer7 and header1 - header4 for arch, footer1 - footer3 and header1 - header3 for typo
    """
    A_FOOTER_FIRST_ZERO = "footer1.xml"
    A_FOOTER_DEFAULT_ZERO = "footer2.xml"
    A_FOOTER_FIRST_ONE = "footer3.xml"
    A_FOOTER_EVEN_ONE_TWO = "footer4.xml"
    A_FOOTER_DEFAULT_ONE_TWO = "footer5.xml"
    A_FOOTER_LANDSCAPE_EVEN = "footer6.xml"
    A_FOOTER_LANDSCAPE_ODD = "footer7.xml"

    A_HEADER_DEFAULT_ZERO_ONE_TWO = "header1.xml"
    A_HEADER_FIRST_ONE = "header2.xml"
    A_HEADER_LANDSCAPE_EVEN = "header3.xml"
    A_HEADER_LANDSCAPE_ODD = "header4.xml"

    T_FOOTER_DEFAULT_ZERO = "footer1.xml"
    T_FOOTER_EVEN_ZERO = "footer2.xml"
    T_FOOTER_EVEN_ONE = "footer3.xml"
    T_FOOTER_DEFAULT_ONE = "footer4.xml"

    T_HEADER_DEFAULT_ZERO = "header1.xml"
    T_HEADER_EVEN_ZERO = "header2.xml"
    T_HEADER_EVEN_ONE = "header3.xml"
    T_HEADER_DEFAULT_ONE = "header4.xml"

    P_FOOTER_DEFAULT_ZERO = "footer1.xml"
    P_FOOTER_FIRST_ONE = "footer2.xml"
    P_FOOTER_EVEN_ONE = "footer3.xml"
    P_FOOTER_DEFAULT_ONE = "footer4.xml"

    P_HEADER_DEFAULT_ZERO = "header1.xml"
    P_HEADER_FIRST_ONE = "header2.xml"
    P_HEADER_EVEN_ONE = "header3.xml"
    P_HEADER_DEFAULT_ONE = "header4.xml"

    def __repr__(self):
        return f"<{self.__class__.__name__}({self._name_})>"

    def __str__(self):
        return f"{self.__class__.__name__}: {self._value_}"


class XmlRelationshipType(Enum):
    """Document relationship type."""
    FOOTER = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer"
    PACKAGE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/package"
    HYPERLINK = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink"
    IMAGE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"
    THEME = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme"
    ENDNOTES = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/endnotes"
    NUMBERING = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering"
    WEB_SETTINGS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/webSettings"
    SETTINGS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings"
    HEADER = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/header"
    STYLES = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles"
    FONT_TABLE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/fontTable"
    FOOTNOTES = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/footnotes"
    OLE_OBJECT = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/oleObject"
    GLOSSARY = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/glossaryDocument"
    KEYMAP_CUSTOMIZATIONS = "http://schemas.microsoft.com/office/2006/relationships/keyMapCustomizations"
    OFFICE_DOCUMENT = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument"
    CUSTOM_PROPERTIES = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/custom-properties"
    CUSTOM_XML = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/customXml"
    HDPHOTO = "http://schemas.microsoft.com/office/2007/relationships/hdphoto"
    CORE_PROPERTIES_PACKAGE = "http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties"
    METADATA_CORE = "http://schemas.openxmlformats.org/officedocument/2006/relationships/metadata/core-properties"
    DIGITAL_SIGNATURE = "http://schemas.openxmlformats.org/package/2006/relationships/digital-signature/signature"
    DS_CERTIFICATE = "http://schemas.openxmlformats.org/package/2006/relationships/digital-signature/certificate"
    DIGITAL_SIGNATURE_ORIGIN = "http://schemas.openxmlformats.org/package/2006/relationships/digital-signature/origin"
    EXTENDED_PROPERTIES = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties"
    EXTENDED_PROPERTIES_PURL = "http://purl.oclc.org/ooxml/officeDocument/relationships/extendedProperties"
    THUMBNAIL = "http://schemas.openxmlformats.org/package/2006/relationships/metadata/thumbnail"
    STYLES_WITH_EFFECTS = "http://schemas.microsoft.com/office/2007/relationships/stylesWithEffects"
    MISSING = ""

    def __repr__(self):
        return f"<{self.__class__.__name__}({self._name_})>"

    def __str__(self):
        return f"{self.__class__.__name__}: {self._value_}"

    @classmethod
    def _missing_(cls, key):
        logger.warning(f"Неизвестное значение RelationshipType {key}")
        return cls.MISSING


class XmlHdrFtrReference(Enum):
    """Document header and footer reference type

    Available options: DEFAULT, EVEN, FIRST.
    """
    DEFAULT = "default"
    EVEN = "even"
    FIRST = "first"

    def __repr__(self):
        return f"<{self.__class__.__name__}({self._name_})>"

    def __str__(self):
        return f"{self.__class__.__name__}: {self._value_}"


class XmlReference(Enum):
    """Document header or footer reference

    Available options: HEADER, FOOTER.
    """
    HEADER = "w:headerReference"
    FOOTER = "w:footerReference"

    def __repr__(self):
        return f"<{self.__class__.__name__}({self._name_})>"

    def __str__(self):
        return f"{self.__class__.__name__}: {self._value_}"


class DocumentMode(Enum):
    """Document page type

    Available options: ARCH, TYPO, PROG.
    """
    ARCH = "arch"
    TYPO = "typo"
    PROG = "prog"

    def __repr__(self):
        return f"<{self.__class__.__name__}({self._name_})>"

    def __str__(self):
        return f"{self.__class__.__name__}: {self._value_}"


class DocumentSide(Enum):
    """Printing type

    Available options: SINGLE, MIRROR.
    """
    SINGLE = "single"
    MIRROR = "mirror"

    def __repr__(self):
        return f"<{self.__class__.__name__}({self._name_})>"

    def __str__(self):
        return f"{self.__class__.__name__}: {self._value_}"


# noinspection PyUnresolvedReferences
class FileItem(NamedTuple):
    """Parameters selected by the user

    Specifies the parameters of the selected files and the formatting mode in the files.

    Attributes:
        path_file (Path): The path to the file
        document_mode (DocumentMode): The flag to set the two-sided formatting
        document_side (DocumentSide): The type of printing
        def_ministry (bool): The flag to use formatting for
        change_list (bool): The flag to add the change list
    """
    path_file: Path
    document_mode: DocumentMode
    document_side: DocumentSide
    def_ministry: bool
    change_list: bool
    approvement_list: bool

    def __str__(self):
        return f"{self.__class__.__name__}: {self.path_file}"

    def __repr__(self):
        return f"<{self.__class__.__name__}({self._asdict().values()})>"


class UserInputValues:
    __slots__ = (
        "_path_files",
        "_document_mode",
        "_document_side",
        "_def_ministry",
        "_change_list",
        "_approvement_list")

    def __init__(
            self,
            path_files: Iterable[Path] | None = None,
            document_mode: DocumentMode | None = None,
            document_side: DocumentSide | None = None,
            def_ministry: TriState = None,
            change_list: TriState = None,
            approvement_list: TriState = None):
        if document_mode is None:
            document_mode = DocumentMode.ARCH
        if path_files is None:
            path_files = []
        if document_side is None:
            document_side = DocumentSide.MIRROR
        if def_ministry is None:
            def_ministry = False
        if change_list is None:
            change_list = False
        if approvement_list is None:
            approvement_list = False

        self._document_mode: DocumentMode = document_mode
        self._path_files: list[Path] = [*path_files]
        self._document_side: DocumentSide = document_side
        self._def_ministry: bool = def_ministry
        self._change_list: bool = change_list
        self._approvement_list: bool = approvement_list

    def to_dict(self):
        return {item.removeprefix("_"): str(getattr(self, item)) for item in self.__slots__}

    def __str__(self):
        _str_dict: str = ", ".join([f"{k} = {v}" for k, v in self.to_dict().items()])
        return f"{self.__class__.__name__}: {_str_dict}"

    def __repr__(self):
        _sep: str = "--------------------"
        _str_dict: str = "\n".join([f"{k} = {v}" for k, v in self.to_dict().items()])
        return f"<{_sep}{self.__class__.__name__}>\n{_str_dict}\n{_sep}"

    def __len__(self):
        return len(self._path_files)

    def __bool__(self):
        return len(self) > 0

    def __hash__(self):
        return hash(tuple(getattr(self, attr) for attr in self.__slots__))

    def __key(self):
        return (
            self._path_files,
            self._document_mode,
            self._document_side,
            self._def_ministry,
            self._change_list,
            self._approvement_list)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__key() == other.__key()

        else:
            return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return self.__key() != other.__key()

        else:
            return NotImplemented

    @property
    def document_mode(self):
        return self._document_mode

    @property
    def path_files(self):
        return self._path_files

    @property
    def document_side(self):
        return self._document_side

    @property
    def def_ministry(self):
        return self._def_ministry

    @property
    def change_list(self):
        return self._change_list

    @property
    def approvement_list(self):
        return self._approvement_list

    @document_mode.setter
    def document_mode(self, value):
        self._document_mode = value

    @path_files.setter
    def path_files(self, value):
        self._path_files = value

    @document_side.setter
    def document_side(self, value):
        self._document_side = value

    @def_ministry.setter
    def def_ministry(self, value):
        self._def_ministry = value

    @change_list.setter
    def change_list(self, value):
        self._change_list = value

    @approvement_list.setter
    def approvement_list(self, value):
        self._approvement_list = value

    def __iter__(self) -> Iterator[FileItem]:
        return iter(
            FileItem(
                path_file,
                self._document_mode,
                self._document_side,
                self._def_ministry,
                self._change_list,
                self._approvement_list)
            for path_file in self._path_files)
