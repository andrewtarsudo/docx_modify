# -*- coding: utf-8 -*-
from pathlib import Path
from typing import Iterator

from loguru import logger

from docx_modify.core_elements.core_zip_file import CoreZipFile
from docx_modify.enum_element import DocumentMode, CompanyName
from docx_modify.exceptions import CollectionItemNotFoundError, InvalidWordFileDirectoryNameError
from docx_modify.const import parent_path
from docx_modify.word_elements.word_file import WordFile, _WordFileHeaderFooter, _WordFileImage, _WordFileMilitary, \
    _WordFileRels


class WordFileCollection:
    dirs = {
        "headers_footers": _WordFileHeaderFooter,
        "image": _WordFileImage,
        "rels": _WordFileRels}

    def __init__(
            self,
            core_zip_file: CoreZipFile,
            document_mode: DocumentMode,
            company_name: CompanyName,
            def_ministry: bool):
        self._core_zip_file: CoreZipFile = core_zip_file
        self._document_mode: DocumentMode = document_mode
        self._def_ministry: bool = def_ministry
        self._company_name: CompanyName = company_name
        self._word_files: list[WordFile] = []

    def __repr__(self):
        return f"<{self.__class__.__name__}({[repr(word_file) for word_file in self._word_files]})>"

    def __str__(self):
        return f"{self.__class__.__name__}: {[word_file.name for word_file in self._word_files]}"

    @property
    def add_path_mode(self) -> str:
        if self.document_mode is not None:
            return self.document_mode.value

        else:
            logger.error("Значение document_mode не задано")
            logger.info(str(self))
            raise ValueError

    @property
    def document_mode(self) -> DocumentMode:
        return self._document_mode

    @property
    def word_files(self) -> list[WordFile]:
        return self._word_files

    @word_files.setter
    def word_files(self, value):
        self._word_files = value

    @property
    def file_names(self) -> list[str]:
        return [word_file.name for word_file in self._word_files]

    def iter_files(self, name: str) -> Iterator[WordFile]:
        if name not in self.dirs:
            logger.error(f"Имя {name} не найдено в списке {self.dirs.keys()}")
            raise InvalidWordFileDirectoryNameError

        else:
            return iter(filter(lambda x: isinstance(x, self.dirs.get(name)), iter(self)))

    def add_to_archive(self, name: str):
        for word_file in self.iter_files(name):
            logger.info(f"Директория {word_file.full_path_zip_archive}")
            name_from: Path = word_file.basic_xml_file
            name_to: Path = word_file.full_path_zip_archive
            self._core_zip_file.copy(name_from, name_to)

            logger.info(f"Файл {name_from} копирован в {name_to}")

    def __iter__(self) -> Iterator[WordFile]:
        return iter(self._word_files)

    def __contains__(self, item):
        return item in iter(self)

    def __getitem__(self, item):
        if isinstance(item, str):
            if item not in self.file_names:
                logger.error(f"Файл {item} не найден")
                raise CollectionItemNotFoundError

            else:
                item: int = self.file_names.index(item)

        return self._word_files[item]

    def __add__(self, other):
        if isinstance(other, WordFile) or issubclass(other.__class__, WordFile):
            self.word_files.append(other)

        elif isinstance(other, self.__class__):
            self._word_files.extend(other._word_files)

        else:
            return NotImplemented

    __radd__ = __add__
    __iadd__ = __add__

    def iter_names(self, name: str):
        return iter(
            _.name for _ in parent_path.joinpath(f"sources/{self.add_path_mode}/{name}/").iterdir())

    def add_word_files(self):
        for _ in self.iter_names("headers_footers"):
            word_file_header_footer: _WordFileHeaderFooter
            word_file_header_footer = _WordFileHeaderFooter(_, self._core_zip_file, self._document_mode)
            self + word_file_header_footer

        for _ in self.iter_names("rels"):
            word_file_rels: _WordFileRels
            word_file_rels = _WordFileRels(_, self._core_zip_file, self._document_mode)
            self + word_file_rels

    def add_word_file_image(self):
        name: str = self._company_name.value
        _: _WordFileImage = _WordFileImage(name, self._core_zip_file, self._document_mode)
        word_file_image: _WordFileImage = _.duplicate()
        self + word_file_image

    def add_word_file_military(self):
        if self._def_ministry:
            word_file_military: _WordFileMilitary
            word_file_military = _WordFileMilitary("footer3.xml", self._core_zip_file, self._document_mode)

            self._core_zip_file.delete(word_file_military.full_path_zip_archive)
            self + word_file_military

            name_from: Path = word_file_military.basic_xml_file
            name_to: Path = word_file_military.full_path_zip_archive
            self._core_zip_file.copy(name_from, name_to)

            logger.success("Нижний колонтитул изменен для поставки МО РФ")
