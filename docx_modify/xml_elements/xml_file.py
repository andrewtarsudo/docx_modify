# -*- coding: utf-8 -*-
from pathlib import Path

from loguru import logger
from lxml import etree
# noinspection PyProtectedMember
from lxml.etree import ElementBase, _ElementTree

from docx_modify.core_elements.core_zip_file import CoreZipFile, UnzippedFile
from docx_modify.exceptions import RequiredXmlFileMissingError
from docx_modify.xml_elements.xml_object import XmlObject


class XmlFile(XmlObject):
    def __init__(self, name: str, core_zip_file: CoreZipFile, default: bytes | None = None):
        super().__init__()
        self._core_zip_file: CoreZipFile = core_zip_file
        self._unzipped_file: UnzippedFile = UnzippedFile(name, core_zip_file)
        self._etree: _ElementTree | None = None
        self._content: ElementBase | None = None
        self._exists: bool | None = None

        if default is not None:
            self._default: bytes = default

    def __str__(self):
        return f"{self.__class__.__name__}: {self._name}"

    def __repr__(self):
        return f"<{self.__class__.__name__}({self._unzipped_file.path})>"

    def __hash__(self):
        return hash(self._name)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return True

        else:
            return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return False

        else:
            return NotImplemented

    @property
    def _name(self) -> str:
        return self._unzipped_file.name

    @property
    def full_path(self) -> Path:
        return self._unzipped_file.full_path

    @property
    def _content_tree(self) -> _ElementTree:
        return self._content.getroottree()

    def write(self, **kwargs):
        self._content_tree.write(self.full_path, encoding="utf-8", doctype=self.DOCTYPE)
        logger.info(f"Файл {self.full_path} записан")

    def read(self, **kwargs):
        if self._unzipped_file.full_path.exists():
            self._etree = etree.parse(self._unzipped_file.full_path)
            self._content = self._etree.getroot()
            self._exists: bool = True

        else:
            if not hasattr(self, "_default"):
                logger.error(f"Файл {self._unzipped_file.name} не найден и не задано содержимое по умолчанию")
                logger.error("Это означает, что необходимо проверить корректность изначального файла")
                raise RequiredXmlFileMissingError

            else:
                self._unzipped_file.full_path.parent.mkdir(parents=True, exist_ok=True)
                self._unzipped_file.full_path.touch(exist_ok=True)
                logger.error(f"Файл {self._unzipped_file.name} не обнаружен, поэтому будет создан файл по умолчанию")

                with open(self.full_path, "wb") as fw:
                    fw.write(self._default)
                    logger.info(f"Файл {self._name} создан")

            self._content = etree.fromstring(self._default)
            self._etree = self._content.getroottree()
            self._exists: bool = False

    def save(self):
        if self._content_tree != self._etree:
            self.write()
            self._etree = self._content_tree

    @property
    def core_zip_file(self):
        return self._core_zip_file

    @property
    def exists(self):
        return self._exists


class XmlFilePart(XmlObject):
    def __init__(self, tag: str, xml_file: XmlFile, idx: int | None = None):
        super().__init__()

        if idx is None:
            idx: int = -1

        self._xml_file: XmlFile = xml_file
        self._tag: str = tag
        self._idx: int = idx
        self._content: ElementBase | None = None
        self._prev_state: ElementBase | None = None

    def __str__(self):
        _idx: str = f"{self._idx}" if self._idx != -1 else ""
        # noinspection PyProtectedMember
        return f"{self.__class__.__name__}: {self._xml_file._name}. {self._tag}{_idx}"

    def __repr__(self):
        return f"<{self.__class__.__name__}({self._tag}, {repr(self._xml_file)}, {self._idx})>"

    def __key(self):
        return self._xml_file.full_path, self._tag, self._idx

    def __hash__(self):
        return hash((self._xml_file.full_path, self._tag, self._idx))

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

    def parent(self) -> ElementBase:
        return self._prev_state.getparent()

    def read(self, **kwargs):
        if self._idx == -1:
            self._prev_state = self._xml_file.get_child(self._tag)
        else:
            self._prev_state = self._xml_file.get_descendants(self._tag)[self._idx]
        self._content = self._prev_state

    def write(self, **kwargs):
        self.parent().replace(self._prev_state, self._content)
        self._prev_state = self._content
