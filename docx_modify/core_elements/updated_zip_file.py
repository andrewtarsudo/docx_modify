# -*- coding: utf-8 -*-
from os import walk
from pathlib import Path
from shutil import rmtree
from typing import TypeAlias
from zipfile import ZIP_DEFLATED, ZipFile

from loguru import logger

from docx_modify.exceptions import FileNotInArchiveError, ZipFileUnzippedError, ZipFileZippedError

PathLike: TypeAlias = str | Path


class UpdatedZipFile:
    def __init__(self, path: PathLike, path_dir: Path | None = None):
        if isinstance(path, str):
            path: Path = Path(path)
        if path_dir is None:
            path_dir: Path = Path.home().joinpath("Desktop").joinpath("_docx_temp")

        self._path: Path = path
        self._zip_file: ZipFile | None = None
        self._is_zipped: bool = True
        self._path_dir: Path = path_dir

    def __repr__(self):
        return f"<{self.__class__.__name__}({self._path})>"

    def __bool__(self):
        return True

    def __len__(self):
        return len(self.files)

    def __key(self):
        return self._path, self._zip_file

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
    def is_zipped(self):
        return self._is_zipped

    @is_zipped.setter
    def is_zipped(self, value):
        self._is_zipped = value

    @property
    def files(self) -> list[str]:
        return self.reader().zip_file.namelist()

    def full_name(self, name: PathLike) -> Path:
        return self._path_dir.joinpath(name)

    def reader(self) -> '_UpdatedZipFileReader':
        return _UpdatedZipFileReader(self._path)

    def writer(self) -> '_UpdatedZipFileWriter':
        return _UpdatedZipFileWriter(self._path)

    def zip_file_manager(self) -> '_UpdatedZipFileManager':
        return _UpdatedZipFileManager(self._path)

    def unarchive(self):
        self._zip_file = self.reader().zip_file

        if not self.is_zipped:
            logger.error("ZIP-архив уже распакован")
            raise ZipFileUnzippedError

        self.is_zipped = False
        return self.reader().unarchive()

    def archive(self):
        if self.is_zipped:
            logger.error("ZIP-архив уже запакован")
            raise ZipFileZippedError

        self.is_zipped = True
        return self.writer().archive()

    def copy_file(self, name_from: PathLike, name_to: PathLike):
        return self.zip_file_manager().copy_file(name_from, name_to)

    def delete_file(self, name: PathLike):
        return self.zip_file_manager().delete_file(name)

    def modify_file(self, name: PathLike, content: bytes):
        return self.zip_file_manager().modify_file(name, content)

    def rename_file(self, file_name: PathLike, new_name: PathLike):
        return self.zip_file_manager().rename_file(file_name, new_name)

    def close(self):
        self._zip_file.close()

    def delete_temp_archive(self):
        if not self.is_zipped:
            self.archive()

        rmtree(self._path_dir, True)

    def __enter__(self):
        if self.is_zipped:
            self.unarchive()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.is_zipped:
            self.archive()

        self.close()


class _UpdatedZipFileReader(UpdatedZipFile):
    def __init__(self, path: PathLike):
        super().__init__(path)
        self._zip_file: ZipFile = ZipFile(self._path, "r", ZIP_DEFLATED)

    def read(self, name: PathLike) -> bytes:
        if isinstance(name, Path):
            name: str = str(name)

        try:
            with self._zip_file as zf:
                content: bytes = zf.read(name)

        except OSError as e:
            logger.error(f"{e.__class__.__name__}, {e.strerror}")
            raise

        else:
            return content

    def unarchive(self):
        self._zip_file = self.reader()._zip_file
        self._path_dir.mkdir(exist_ok=True)
        self._zip_file.extractall(self._path_dir)

    @property
    def zip_file(self):
        return self._zip_file


class _UpdatedZipFileWriter(UpdatedZipFile):
    def __init__(self, path: PathLike):
        super().__init__(path)
        self._zip_file: ZipFile = ZipFile(self._path, "w", ZIP_DEFLATED)

    def write(self, name: PathLike, text: str | bytes):
        if isinstance(name, Path):
            name: str = str(name)

        if name not in self.files:
            logger.error(f"Файл или директория {name} не найдено в архиве")
            raise FileNotInArchiveError

        try:
            with self._zip_file as zf:
                zf.writestr(name, text, ZIP_DEFLATED)

        except OSError as e:
            logger.error(f"{e.__class__.__name__}, {e.strerror}")
            raise

    def archive(self):
        with self._zip_file as zf:
            for dirpath, _, filenames in walk(self._path_dir):
                for f in filenames:
                    filename: Path = Path(dirpath).joinpath(f)
                    arcname: Path = filename.relative_to(self._path_dir)
                    zf.write(filename, arcname)


class _UpdatedZipFileManager(UpdatedZipFile):
    def delete_file(self, name: PathLike):
        try:
            self.full_name(name).unlink(missing_ok=True)

        except RuntimeError as e:
            logger.error(f"{e.__class__.__name__}, {str(e)}")
            raise

        except OSError as e:
            logger.error(f"{e.__class__.__name__}, {e.strerror}")
            raise

    def copy_file(self, name_from: PathLike, name_to: PathLike):
        try:
            with open(name_from, "rb") as fb_read:
                content: bytes = fb_read.read()

            with open(name_to, "wb") as fb_write:
                fb_write.write(content)

        except NotADirectoryError | FileNotFoundError | PermissionError as e:
            logger.error(f"{e.__class__.__name__}, {e.strerror}")
            raise

        except RuntimeError as e:
            logger.error(f"{e.__class__.__name__}, {str(e)}")
            raise

        except OSError as e:
            logger.error(f"{e.__class__.__name__}, {e.strerror}")
            raise
