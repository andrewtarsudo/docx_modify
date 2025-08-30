# -*- coding: utf-8 -*-
from pathlib import Path
from typing import TypeAlias, Literal, Any

try:
    from tomllib import load
except ModuleNotFoundError:
    # noinspection PyUnresolvedReferences
    from tomli import load

_MIRROR_ARCH_FORMULA: str = """\
<w:p xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:pPr>
    <w:pStyle w:val="_style_table_11_" />
  </w:pPr>
  <w:r>
    <w:fldChar w:fldCharType="begin" />
  </w:r>
  <w:r>
    <w:instrText xml:space="preserve"> =ROUND(</w:instrText>
  </w:r>
  <w:r>
    <w:fldChar w:fldCharType="begin" />
  </w:r>
  <w:r>
    <w:instrText xml:space="preserve"> NUMPAGES \* MERGEFORMAT </w:instrText>
  </w:r>
  <w:r>
    <w:fldChar w:fldCharType="separate" />
  </w:r>
  <w:r>
    <w:instrText>0</w:instrText>
  </w:r>
  <w:r>
    <w:fldChar w:fldCharType="end" />
  </w:r>
  <w:r>
    <w:instrText xml:space="preserve"> *0,5; 0 ) </w:instrText>
  </w:r>
  <w:r>
    <w:fldChar w:fldCharType="separate" />
  </w:r>
  <w:r>
    <w:t>0</w:t>
  </w:r>
  <w:r>
    <w:fldChar w:fldCharType="end" />
  </w:r>
</w:p>
"""

_SINGLE_ARCH_FORMULA: str = """\
<w:p xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:pPr>
    <w:pStyle w:val="_style_table_11_"/>
  </w:pPr>
  <w:r>
    <w:fldChar w:fldCharType="begin"/>
  </w:r>
  <w:r>
    <w:instrText xml:space="preserve"> NUMPAGES \* MERGEFORMAT </w:instrText>
  </w:r>
  <w:r>
    <w:fldChar w:fldCharType="separate"/>
  </w:r>
  <w:r>
    <w:t>0</w:t>
  </w:r>
  <w:r>
    <w:fldChar w:fldCharType="end"/>
  </w:r>
</w:p>\
"""

parent_path: Path = Path(__file__).parent.parent
temp_path: Path = Path.home().joinpath("Desktop")
log_folder: Path = temp_path.joinpath("_docx_logs")

TriState: TypeAlias = bool | None
HeaderFooter: TypeAlias = Literal["header", "footer"]


def version():
    with open(parent_path.joinpath("pyproject.toml"), "rb") as f:
        content: dict[str, Any] = load(f)

    return content.get("project").get("version")
