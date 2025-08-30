# -*- coding: utf-8 -*-
from functools import cached_property
from glob import iglob
from pathlib import Path

from loguru import logger

from docx_modify.core_elements.core_document import CoreDocument
from docx_modify.core_elements.updated_zip_file import PathLike, UpdatedZipFile
from docx_modify.exceptions import FileNotInArchiveError


class UnzippedFile:
    def __init__(self, name: str, core_zip_file: 'CoreZipFile'):
        self._name: str = name
        self._core_zip_file: 'CoreZipFile' = core_zip_file

    def __repr__(self):
        return f"<{self.__class__.__name__}({self._name}, {repr(self._core_zip_file)})>," \
               f" {self._core_zip_file.path}"

    def __str__(self):
        return f"{self.__class__.__name__}: {self._name}, {str(self._core_zip_file)}, {self._core_zip_file.path}"

    @cached_property
    def path_dir(self):
        return self._core_zip_file.path_dir

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @cached_property
    def path(self) -> Path:
        return self._core_zip_file.path

    @property
    def full_path(self) -> Path:
        """The full path to the file in the unpacked archive."""
        return self.path_dir.joinpath(self.name)

    def __hash__(self):
        return hash(self._name)

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

    @property
    def core_zip_file(self):
        return self._core_zip_file


class CoreZipFile:
    def __init__(self, core_document: CoreDocument):
        self._core_document: CoreDocument = core_document
        self.__updated_zip_file: UpdatedZipFile = UpdatedZipFile(core_document.path, core_document.path_dir)
        self._is_zipped: bool = True

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.path})>, {repr(self.__updated_zip_file)}, {self._is_zipped}"

    def __str__(self):
        return f"{self.__class__.__name__}: {self.path}, {str(self.__updated_zip_file)}"

    def copy(self, name_from: PathLike, name_to: PathLike):
        return self.__updated_zip_file.copy_file(name_from, name_to)

    @property
    def files(self) -> list[str]:
        return self.__updated_zip_file.files

    def unarchive(self):
        return self.__updated_zip_file.unarchive()

    def delete(self, name: PathLike):
        self.__updated_zip_file.delete_file(name)

    def delete_temp_archive(self):
        return self.__updated_zip_file.delete_temp_archive()

    def delete_files(self, pattern: str):
        for file in iglob(pattern, root_dir=self.path_dir, recursive=False):
            self.delete(file)
            logger.info(f"Файл {file} удален")

    def __getitem__(self, item):
        if item in self:
            _index: int = self.files.index(item)
            return self.files[_index]

        elif item in self.unzipped_files:
            return self.unzipped_files.get(item)

        else:
            logger.error(f"Файл {item} не найден в разархивированном ZIP-пакете")
            raise FileNotInArchiveError

    def __iter__(self):
        return iter(self.files)

    def __contains__(self, item):
        return item in iter(self)

    def __len__(self):
        return len(self.files)

    def __bool__(self):
        return self._is_zipped

    def name_updated(self):
        return self._core_document.name_updated

    @property
    def unzipped_files(self) -> dict[str, UnzippedFile]:
        return {name: UnzippedFile(name, self) for name in self.files}

    def __enter__(self):
        self.__updated_zip_file = self.__updated_zip_file.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__updated_zip_file.__exit__(exc_type, exc_val, exc_tb)
        self.__updated_zip_file.close()

    @property
    def path(self):
        return self._core_document.path

    @property
    def path_dir(self):
        return self._core_document.path_dir
