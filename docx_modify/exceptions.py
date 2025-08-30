# -*- coding: utf-8 -*-
class BaseError(Exception):
    """Base error class to inherit."""


class BaseArchiveError(BaseError):
    """Base error class for zip archive instances to inherit."""


class FileNotInArchiveError(BaseArchiveError):
    """File is not found in the archive."""


class ZipFileZippedError(BaseArchiveError):
    """Zip file is zipped."""


class ZipFileUnzippedError(BaseArchiveError):
    """Zip file is unzipped."""


class CollectionItemNotFoundError(BaseError):
    """File is not found in the Word file collection."""


class InvalidOrientationError(BaseError):
    """Unknown type of section orientation."""


class InvalidPythonVersion(BaseError):
    """Installed Python version is outdated."""


class InvalidOptionError(BaseError):
    """Received option is not proper."""


class InvalidWordFileDirectoryNameError(BaseError):
    """WordFile directory name is not proper."""


class InvalidXmlElementError(BaseError):
    """XML element does not have proper attributes."""


class InvalidXmlFileError(BaseError):
    """XML file is not valid."""


class RequiredXmlFileMissingError(BaseError):
    """XML file must be in the archive, but it is missing."""


class WidgetNotFoundError(BaseError):
    """Widget having the specified name is missing."""
