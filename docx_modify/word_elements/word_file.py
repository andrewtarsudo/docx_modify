# -*- coding: utf-8 -*-
from pathlib import Path
from shutil import copy2

from docx_modify.core_elements.core_zip_file import CoreZipFile, UnzippedFile
from docx_modify.enum_element import DocumentMode
from docx_modify.const import parent_path


class WordFile(UnzippedFile):
    def __init__(self, name: str, core_zip_file: CoreZipFile, document_mode: DocumentMode):
        super().__init__(name, core_zip_file)
        self._document_mode: DocumentMode = document_mode

    def __repr__(self):
        return f"<{self.__class__.__name__}({self._name}, {self._core_zip_file}, {self.basic_xml_file})>"

    def __str__(self):
        return f"{self.__class__.__name__}: {self.full_path}, {self.basic_xml_file}"

    @property
    def basic_file_path(self) -> Path:
        raise NotImplementedError

    @property
    def basic_xml_file(self) -> Path:
        return self.basic_file_path.joinpath(self._name)

    @property
    def full_path_zip_archive(self) -> Path:
        return self.path_dir.joinpath(self.zip_archive_folder).joinpath(self._name)

    @property
    def zip_archive_folder(self):
        raise NotImplementedError

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._name == other._name

        else:
            return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return self._name != other._name

        else:
            return NotImplemented

    def __hash__(self):
        return hash(self._name)

    @property
    def add_path_mode(self):
        return self._document_mode.value


class _WordFileHeaderFooter(WordFile):
    @property
    def basic_file_path(self) -> Path:
        return parent_path.joinpath(f"sources/{self.add_path_mode}/headers_footers/")

    @property
    def zip_archive_folder(self) -> str:
        return "word"


class _WordFileImage(WordFile):
    @property
    def basic_file_path(self) -> Path:
        return parent_path.joinpath("sources/image/")

    @property
    def zip_archive_folder(self) -> str:
        return "word/media"

    def duplicate(self):
        src: Path = self.basic_xml_file
        dst: Path = self.basic_xml_file.with_name("_logo.png")
        copy2(src, dst)
        return self.__class__(dst.name, self._core_zip_file, self._document_mode)


class _WordFileRels(WordFile):
    @property
    def basic_file_path(self) -> Path:
        return parent_path.joinpath(f"sources/{self.add_path_mode}/rels/")

    @property
    def zip_archive_folder(self) -> str:
        return "word/_rels"


class _WordFileMilitary(WordFile):
    @property
    def basic_file_path(self) -> Path:
        return parent_path.joinpath("sources/military/")

    @property
    def zip_archive_folder(self) -> str:
        return "word"
