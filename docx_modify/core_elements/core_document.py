# -*- coding: utf-8 -*-
from pathlib import Path
from shutil import copy2

from loguru import logger

from docx_modify.const import temp_path
from docx_modify.core_elements.clark_name import register_ns
from docx_modify.core_elements.updated_zip_file import PathLike


class CoreDocument:
    def __init__(self, path: PathLike):
        if isinstance(path, str):
            path: Path = Path(path).resolve()
        self._path: Path = path
        self.path_dir: Path = temp_path.joinpath("_docx_temp")
        self._name_updated: str | None = None
        register_ns()

    def __repr__(self):
        return f"<{self.__class__.__name__}({self._path})>"

    def __str__(self):
        return f"{self.__class__.__name__}: {self._path}"

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._path == other._path

        else:
            return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return self._path != other._path

        else:
            return NotImplemented

    def __hash__(self):
        return hash(self._path)

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._path = value

    def _new_name(self, name: str) -> Path:
        return self._path.with_stem(f"{self._path.stem}_{name}")

    def _prepare_file(self, name: str) -> Path:
        _new_file: Path = self._new_name(name)

        if not _new_file.exists():
            logger.success(f"Имя {_new_file.name} доступно")
            return _new_file

        else:
            logger.info(f"Файл {_new_file.name} уже существует")
            logger.warning(f"Проверка имени {name}_new ...")
            return self._prepare_file(f"{name}_new")

    def duplicate(self, name: str):
        _new_file: Path = self._prepare_file(name)
        self._name_updated = f"{_new_file}"
        _origin_file_name: Path = self._path

        try:
            self._path.rename(_new_file)
            self._path = _new_file
            copy2(self._path, _origin_file_name)

        except PermissionError as e:
            logger.error(f"Файл {self._path.name} не может быть переименован в {_new_file.name}")
            logger.error(f"{e.__class__.__name__}, {e.strerror}")
            raise

        except OSError as e:
            logger.error(f"{e.__class__.__name__}, {e.strerror}")
            raise

    @property
    def name_updated(self):
        return self._name_updated
