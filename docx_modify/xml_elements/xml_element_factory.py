# -*- coding: utf-8 -*-
from typing import Any, Iterable, Mapping

from lxml.etree import Element, ElementBase

from docx_modify.core_elements.clark_name import fqdn


def new_xml(
        tag: str, *,
        children: Iterable[ElementBase] | None = None,
        attributes: Mapping[str, Any] | None = None) -> ElementBase:
    if children is None:
        children: list[ElementBase] = []

    if attributes is None:
        attributes: dict[str, str] = {}

    _attrs: dict[str, str] = {fqdn(k): f"{v}" for k, v in attributes.items()}

    if not _attrs:
        element: ElementBase = Element(fqdn(tag))

    else:
        element: ElementBase = Element(fqdn(tag), _attrs)

    element.extend(children)
    return element


def new_xml_no_ns(
        tag: str, *,
        children: Iterable[ElementBase] | None = None,
        attributes: Mapping[str, Any] | None = None):
    if children is None:
        children: list[ElementBase] = []
    if attributes is None:
        attributes: dict[str, Any] = {}

    _attrs: dict[str, Any] = {k: f"{v}" for k, v in attributes.items()}

    if not _attrs:
        element: ElementBase = Element(tag)

    else:
        element: ElementBase = Element(tag, _attrs)

    element.extend(children)
    return element
