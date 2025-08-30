# -*- coding: utf-8 -*-
from typing import Iterable, NamedTuple

from docx_modify.enum_element import TriState, XmlHdrFtrReference, XmlReference, XmlRelationshipTarget, \
    XmlRelationshipType, DocumentMode


class HdrFtrReference(NamedTuple):
    reference: XmlReference
    rid: str
    ref_type: XmlHdrFtrReference

    def __str__(self):
        return f"{self.__class__.__name__}: {self.reference.value}, {self.rid}, {self.ref_type}"

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.reference.value}, {self.rid}, {self.ref_type})>"


class _HdrFtrRelationshipReference(NamedTuple):
    name: str
    section_index: int
    rel_target: XmlRelationshipTarget
    reference: XmlReference
    reference_type: XmlHdrFtrReference
    rel_type: XmlRelationshipType

    def __str__(self):
        return f"{self.__class__.__name__}: {self._asdict().values()}"

    def __repr__(self):
        return f"<{self.__class__.__name__}({self._asdict().items()})>"

    def hdr_ftr_reference(self, rel_id: str) -> HdrFtrReference:
        return HdrFtrReference(self.reference, rel_id, self.reference_type)


class HdrFtrRelReferenceController(dict):
    def __init__(
            self, *,
            document_mode: DocumentMode,
            def_ministry: TriState = None,
            hdr_ftr_items: Iterable[_HdrFtrRelationshipReference] = None):
        if def_ministry is None:
            def_ministry = False

        super().__init__()
        self._document_mode: DocumentMode = document_mode
        self._def_ministry: bool = def_ministry

        if hdr_ftr_items is not None:
            for hdr_ftr in hdr_ftr_items:
                self[hdr_ftr.name] = hdr_ftr

    @property
    def rel_target_rel_type(self) -> dict[XmlRelationshipTarget, XmlRelationshipType]:
        return {rel_ref.rel_target: rel_ref.rel_type for rel_ref in self.values()}

    def _generate_hdr_ftr(
            self,
            name: str,
            section_index: int,
            rel_target: XmlRelationshipTarget,
            reference: XmlReference,
            reference_type: XmlHdrFtrReference,
            rel_type: XmlRelationshipType):
        hdr_ftr: _HdrFtrRelationshipReference
        hdr_ftr = _HdrFtrRelationshipReference(
            name, section_index, rel_target, reference, reference_type, rel_type)
        self[name] = hdr_ftr

    def section_hdr_ftr(self, section_index: int) -> list[_HdrFtrRelationshipReference]:
        return list(filter(lambda x: x.section_index == section_index, self.values()))

    def generate_all(self):
        raise NotImplementedError

    def make_hdr_ftr_rel_ref_mode(self):
        if self._document_mode == DocumentMode.ARCH:
            return HdrFtrRelRefArch(
                document_mode=DocumentMode.ARCH,
                def_ministry=self._def_ministry,
                hdr_ftr_items=self.values())

        elif self._document_mode == DocumentMode.TYPO:
            return HdrFtrRelRefTypo(
                document_mode=DocumentMode.TYPO,
                def_ministry=self._def_ministry,
                hdr_ftr_items=self.values())

        elif self._document_mode == DocumentMode.PROG:
            return HdrFtrRelRefProg(
                document_mode=DocumentMode.PROG,
                def_ministry=self._def_ministry,
                hdr_ftr_items=self.values())


class HdrFtrRelRefArch(HdrFtrRelReferenceController):
    def generate_all(self):
        # ==================== Zero section ==================== #

        # -------------------- Footers -------------------- #
        self._generate_hdr_ftr(
            "zero_first_footer", 0,
            XmlRelationshipTarget.A_FOOTER_FIRST_ZERO,
            XmlReference.FOOTER,
            XmlHdrFtrReference.FIRST,
            XmlRelationshipType.FOOTER)
        self._generate_hdr_ftr(
            "zero_even_footer", 0,
            XmlRelationshipTarget.A_FOOTER_DEFAULT_ZERO,
            XmlReference.FOOTER,
            XmlHdrFtrReference.EVEN,
            XmlRelationshipType.FOOTER)
        self._generate_hdr_ftr(
            "zero_default_footer", 0,
            XmlRelationshipTarget.A_FOOTER_DEFAULT_ZERO,
            XmlReference.FOOTER,
            XmlHdrFtrReference.DEFAULT,
            XmlRelationshipType.FOOTER)
        # -------------------- Footers -------------------- #

        # -------------------- Headers -------------------- #
        self._generate_hdr_ftr(
            "zero_first_header", 0,
            XmlRelationshipTarget.A_HEADER_DEFAULT_ZERO_ONE_TWO,
            XmlReference.HEADER,
            XmlHdrFtrReference.FIRST,
            XmlRelationshipType.HEADER)
        self._generate_hdr_ftr(
            "zero_default_header", 0,
            XmlRelationshipTarget.A_HEADER_DEFAULT_ZERO_ONE_TWO,
            XmlReference.HEADER,
            XmlHdrFtrReference.DEFAULT,
            XmlRelationshipType.HEADER)
        # -------------------- Headers -------------------- #

        # ==================== Zero section ==================== #

        # ==================== First section ==================== #

        # -------------------- Headers -------------------- #
        self._generate_hdr_ftr(
            "one_even_header", 1,
            XmlRelationshipTarget.A_HEADER_LANDSCAPE_EVEN,
            XmlReference.HEADER,
            XmlHdrFtrReference.EVEN,
            XmlRelationshipType.HEADER)
        self._generate_hdr_ftr(
            "one_default_header", 1,
            XmlRelationshipTarget.A_HEADER_LANDSCAPE_EVEN,
            XmlReference.HEADER,
            XmlHdrFtrReference.DEFAULT,
            XmlRelationshipType.HEADER)
        self._generate_hdr_ftr(
            "one_first_header", 1,
            XmlRelationshipTarget.A_HEADER_FIRST_ONE,
            XmlReference.HEADER,
            XmlHdrFtrReference.FIRST,
            XmlRelationshipType.HEADER)
        # -------------------- Headers -------------------- #

        # -------------------- Footers -------------------- #
        self._generate_hdr_ftr(
            "one_first_footer", 1,
            XmlRelationshipTarget.A_FOOTER_FIRST_ONE,
            XmlReference.FOOTER,
            XmlHdrFtrReference.FIRST,
            XmlRelationshipType.FOOTER)
        self._generate_hdr_ftr(
            "one_even_footer", 1,
            XmlRelationshipTarget.A_FOOTER_EVEN_ONE_TWO,
            XmlReference.FOOTER,
            XmlHdrFtrReference.EVEN,
            XmlRelationshipType.FOOTER)
        self._generate_hdr_ftr(
            "one_odd_footer", 1,
            XmlRelationshipTarget.A_FOOTER_DEFAULT_ONE_TWO,
            XmlReference.FOOTER,
            XmlHdrFtrReference.DEFAULT,
            XmlRelationshipType.FOOTER)
        # -------------------- Footers -------------------- #

        # ==================== First section ==================== #

        # ==================== Second section ==================== #

        # -------------------- Footers -------------------- #
        self._generate_hdr_ftr(
            "two_even_footer", 2,
            XmlRelationshipTarget.A_FOOTER_EVEN_ONE_TWO,
            XmlReference.FOOTER,
            XmlHdrFtrReference.EVEN,
            XmlRelationshipType.FOOTER)
        self._generate_hdr_ftr(
            "two_odd_footer", 2,
            XmlRelationshipTarget.A_FOOTER_DEFAULT_ONE_TWO,
            XmlReference.FOOTER,
            XmlHdrFtrReference.DEFAULT,
            XmlRelationshipType.FOOTER)
        # -------------------- Footers -------------------- #

        # -------------------- Headers -------------------- #
        self._generate_hdr_ftr(
            "two_even_header", 2,
            XmlRelationshipTarget.A_HEADER_LANDSCAPE_EVEN,
            XmlReference.HEADER,
            XmlHdrFtrReference.EVEN,
            XmlRelationshipType.HEADER)
        self._generate_hdr_ftr(
            "two_odd_header", 2,
            XmlRelationshipTarget.A_HEADER_LANDSCAPE_EVEN,
            XmlReference.HEADER,
            XmlHdrFtrReference.DEFAULT,
            XmlRelationshipType.HEADER)
        # -------------------- Headers -------------------- #

        # ==================== Second section ==================== #

        # -------------------- Footers -------------------- #
        self._generate_hdr_ftr(
            "footer_landscape_even", -1,
            XmlRelationshipTarget.A_FOOTER_LANDSCAPE_EVEN,
            XmlReference.FOOTER,
            XmlHdrFtrReference.EVEN,
            XmlRelationshipType.FOOTER)
        self._generate_hdr_ftr(
            "footer_landscape_odd", -1,
            XmlRelationshipTarget.A_FOOTER_LANDSCAPE_ODD,
            XmlReference.FOOTER,
            XmlHdrFtrReference.DEFAULT,
            XmlRelationshipType.FOOTER)
        # -------------------- Footers -------------------- #

        # -------------------- Headers -------------------- #
        self._generate_hdr_ftr(
            "header_landscape_even", -1,
            XmlRelationshipTarget.A_HEADER_LANDSCAPE_EVEN,
            XmlReference.HEADER,
            XmlHdrFtrReference.EVEN,
            XmlRelationshipType.HEADER)
        self._generate_hdr_ftr(
            "header_landscape_odd", -1,
            XmlRelationshipTarget.A_HEADER_LANDSCAPE_ODD,
            XmlReference.HEADER,
            XmlHdrFtrReference.DEFAULT,
            XmlRelationshipType.HEADER)
        # -------------------- Headers -------------------- #


class HdrFtrRelRefTypo(HdrFtrRelReferenceController):
    def generate_all(self):
        # ==================== Zero section ==================== #

        # -------------------- Footers -------------------- #
        self._generate_hdr_ftr(
            "zero_first_footer", 0,
            XmlRelationshipTarget.T_FOOTER_DEFAULT_ZERO,
            XmlReference.FOOTER,
            XmlHdrFtrReference.FIRST,
            XmlRelationshipType.FOOTER)
        self._generate_hdr_ftr(
            "zero_default_footer", 0,
            XmlRelationshipTarget.T_FOOTER_DEFAULT_ONE,
            XmlReference.FOOTER,
            XmlHdrFtrReference.DEFAULT,
            XmlRelationshipType.FOOTER)
        # -------------------- Footers -------------------- #

        # -------------------- Headers -------------------- #
        self._generate_hdr_ftr(
            "zero_first_header", 0,
            XmlRelationshipTarget.T_HEADER_DEFAULT_ZERO,
            XmlReference.HEADER,
            XmlHdrFtrReference.FIRST,
            XmlRelationshipType.HEADER)
        self._generate_hdr_ftr(
            "zero_even_header", 0,
            XmlRelationshipTarget.T_HEADER_EVEN_ZERO,
            XmlReference.HEADER,
            XmlHdrFtrReference.EVEN,
            XmlRelationshipType.HEADER)
        self._generate_hdr_ftr(
            "zero_default_header", 0,
            XmlRelationshipTarget.T_HEADER_DEFAULT_ONE,
            XmlReference.HEADER,
            XmlHdrFtrReference.DEFAULT,
            XmlRelationshipType.HEADER)
        # -------------------- Headers -------------------- #

        # ==================== Zero section ==================== #

        # ==================== First section ==================== #

        # -------------------- Headers -------------------- #
        self._generate_hdr_ftr(
            "one_even_header", 1,
            XmlRelationshipTarget.T_HEADER_EVEN_ONE,
            XmlReference.HEADER,
            XmlHdrFtrReference.EVEN,
            XmlRelationshipType.HEADER)
        self._generate_hdr_ftr(
            "one_first_header", 1,
            XmlRelationshipTarget.T_HEADER_EVEN_ONE,
            XmlReference.HEADER,
            XmlHdrFtrReference.FIRST,
            XmlRelationshipType.HEADER)
        self._generate_hdr_ftr(
            "one_default_header", 1,
            XmlRelationshipTarget.T_HEADER_DEFAULT_ONE,
            XmlReference.HEADER,
            XmlHdrFtrReference.DEFAULT,
            XmlRelationshipType.HEADER)
        # -------------------- Headers -------------------- #

        # -------------------- Footers -------------------- #
        self._generate_hdr_ftr(
            "one_even_footer", 1,
            XmlRelationshipTarget.T_FOOTER_EVEN_ONE,
            XmlReference.FOOTER,
            XmlHdrFtrReference.EVEN,
            XmlRelationshipType.FOOTER)
        self._generate_hdr_ftr(
            "one_first_footer", 1,
            XmlRelationshipTarget.T_FOOTER_EVEN_ONE,
            XmlReference.FOOTER,
            XmlHdrFtrReference.FIRST,
            XmlRelationshipType.FOOTER)
        self._generate_hdr_ftr(
            "one_odd_footer", 1,
            XmlRelationshipTarget.T_FOOTER_DEFAULT_ONE,
            XmlReference.FOOTER,
            XmlHdrFtrReference.DEFAULT,
            XmlRelationshipType.FOOTER)
        # -------------------- Footers -------------------- #

        # ==================== First section ==================== #

        # ==================== Second section ==================== #

        # -------------------- Footers -------------------- #
        self._generate_hdr_ftr(
            "two_even_footer", 2,
            XmlRelationshipTarget.T_FOOTER_EVEN_ONE,
            XmlReference.FOOTER,
            XmlHdrFtrReference.EVEN,
            XmlRelationshipType.FOOTER)
        self._generate_hdr_ftr(
            "two_odd_footer", 2,
            XmlRelationshipTarget.T_FOOTER_DEFAULT_ONE,
            XmlReference.FOOTER,
            XmlHdrFtrReference.DEFAULT,
            XmlRelationshipType.FOOTER)
        # -------------------- Footers -------------------- #

        # -------------------- Headers -------------------- #
        self._generate_hdr_ftr(
            "two_even_header", 2,
            XmlRelationshipTarget.T_HEADER_EVEN_ONE,
            XmlReference.HEADER,
            XmlHdrFtrReference.EVEN,
            XmlRelationshipType.HEADER)
        self._generate_hdr_ftr(
            "two_odd_header", 2,
            XmlRelationshipTarget.T_HEADER_DEFAULT_ONE,
            XmlReference.HEADER,
            XmlHdrFtrReference.DEFAULT,
            XmlRelationshipType.HEADER)
        # -------------------- Headers -------------------- #

        # ==================== Second section ==================== #


class HdrFtrRelRefProg(HdrFtrRelReferenceController):
    def generate_all(self):
        # ==================== Zero section ==================== #

        # -------------------- Footers -------------------- #
        self._generate_hdr_ftr(
            "zero_first_footer", 0,
            XmlRelationshipTarget.P_FOOTER_DEFAULT_ZERO,
            XmlReference.FOOTER,
            XmlHdrFtrReference.FIRST,
            XmlRelationshipType.FOOTER)
        self._generate_hdr_ftr(
            "zero_default_footer", 0,
            XmlRelationshipTarget.P_FOOTER_DEFAULT_ZERO,
            XmlReference.FOOTER,
            XmlHdrFtrReference.DEFAULT,
            XmlRelationshipType.FOOTER)
        # -------------------- Footers -------------------- #

        # -------------------- Headers -------------------- #
        self._generate_hdr_ftr(
            "zero_first_header", 0,
            XmlRelationshipTarget.P_HEADER_DEFAULT_ZERO,
            XmlReference.HEADER,
            XmlHdrFtrReference.FIRST,
            XmlRelationshipType.HEADER)
        self._generate_hdr_ftr(
            "zero_default_header", 0,
            XmlRelationshipTarget.P_HEADER_DEFAULT_ZERO,
            XmlReference.HEADER,
            XmlHdrFtrReference.DEFAULT,
            XmlRelationshipType.HEADER)
        # -------------------- Headers -------------------- #

        # ==================== Zero section ==================== #

        # ==================== First section ==================== #

        # -------------------- Headers -------------------- #
        self._generate_hdr_ftr(
            "one_even_header", 1,
            XmlRelationshipTarget.P_HEADER_EVEN_ONE,
            XmlReference.HEADER,
            XmlHdrFtrReference.EVEN,
            XmlRelationshipType.HEADER)
        self._generate_hdr_ftr(
            "one_first_header", 1,
            XmlRelationshipTarget.P_HEADER_FIRST_ONE,
            XmlReference.HEADER,
            XmlHdrFtrReference.FIRST,
            XmlRelationshipType.HEADER)
        self._generate_hdr_ftr(
            "one_default_header", 1,
            XmlRelationshipTarget.P_HEADER_DEFAULT_ONE,
            XmlReference.HEADER,
            XmlHdrFtrReference.DEFAULT,
            XmlRelationshipType.HEADER)
        # -------------------- Headers -------------------- #

        # -------------------- Footers -------------------- #
        self._generate_hdr_ftr(
            "one_even_footer", 1,
            XmlRelationshipTarget.P_FOOTER_EVEN_ONE,
            XmlReference.FOOTER,
            XmlHdrFtrReference.EVEN,
            XmlRelationshipType.FOOTER)
        self._generate_hdr_ftr(
            "one_first_footer", 1,
            XmlRelationshipTarget.P_FOOTER_FIRST_ONE,
            XmlReference.FOOTER,
            XmlHdrFtrReference.FIRST,
            XmlRelationshipType.FOOTER)
        self._generate_hdr_ftr(
            "one_odd_footer", 1,
            XmlRelationshipTarget.P_FOOTER_DEFAULT_ONE,
            XmlReference.FOOTER,
            XmlHdrFtrReference.DEFAULT,
            XmlRelationshipType.FOOTER)
        # -------------------- Footers -------------------- #

        # ==================== First section ==================== #
