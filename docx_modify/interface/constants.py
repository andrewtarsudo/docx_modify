# -*- coding: utf-8 -*-
from pathlib import Path
from tkinter.filedialog import askopenfilenames
from tkinter.ttk import Button, Frame
from typing import Callable, NamedTuple

from loguru import logger

from docx_modify.enum_element import DocumentSide

root_title: str = "Конвертация файлов"
ask_directory_title: str = "Выберите файлы для обработки:"
def_ministry_title: str = "Поставка для Министерства Обороны РФ?"
change_list_title: str = "Добавить Лист регистрации изменений в конец документа?"
approvement_list_title: str = "Добавить штамп Листа утверждения на титульный лист?"

button_names: dict[str, str] = {
    "ok": "Ok",
    "cancel": "Отмена"}

document_text_value: dict[str, tuple[tuple[str, int], ...]] = {
    "document_mode": (
        ("Типографский", 0),
        ("Архивный", 1),
        ("Программный", 2)),
    "document_side": (
        ("Для односторонней печати", 0),
        ("Для двусторонней печати", 1))}

root_geometry: str = "800x300"

frame_radiobutton_geometry: dict[str, int] = {
    "width": 780,
    "height": 50}

frame_checkbutton_geometry: dict[str, int] = {
    "width": 520,
    "height": 130}

frame_button_geometry: dict[str, int] = {
    "width": 230,
    "height": 30}

checkbutton_geometry: dict[str, int] = {
    "width": 500}

place_radiobutton_left: dict[str, int] = {
    "x": 10,
    "y": 10}

place_radiobutton_center: dict[str, int] = {
    "x": 260,
    "y": 10}

place_radiobutton_right: dict[str, int] = {
    "x": 520,
    "y": 10}

place_change_list: dict[str, int] = {
    "x": 10,
    "y": 50}

place_def_ministry: dict[str, int] = {
    "x": 10,
    "y": 10}

place_approvement_list: dict[str, int] = {
    "x": 10,
    "y": 90}

place_ok: dict[str, int] = {
    "x": 0,
    "y": 0}

place_cancel: dict[str, int] = {
    "x": 120,
    "y": 0}

place_document_mode: dict[str, int] = {
    "x": 20,
    "y": 20}

place_document_side: dict[str, int] = {
    "x": 20,
    "y": 70}

place_checkbuttons: dict[str, int] = {
    "x": 20,
    "y": 120}

place_buttons: dict[str, int] = {
    "x": 560,
    "y": 250}

_dict_document_side_cb: dict[int, DocumentSide] = {
    0: DocumentSide.SINGLE,
    1: DocumentSide.MIRROR}


def null_command():
    """
    The command for radiobuttons and checkbuttons.

    """
    pass


class CustomButton(Button):
    """
    The generation of the specialized button.

    Parameters
    ----------
    frame : Frame
        The frame to add the button.
    command : Callable
        The command to invoke.
    name : str
        The internal name in the root window.

    Returns
    -------
    Button
        The custom button, Ok or Cancel.

    """

    def __init__(self, frame: Frame, command: Callable, name: str):
        super().__init__(
            frame,
            command=command,
            default="normal",
            name=name,
            style="b.TButton",
            text=button_names.get(name),
            padding=[5, 5, 5, 5])


def get_files() -> tuple[str, ...] | None:
    filetypes: tuple[tuple[str, str], ...] = (
        ("Word files", "*.docx *.docm"),
        ("Docx files", "*.docx"),
        ("Docm files", "*.docm"))

    initialdir: Path = Path.home().joinpath("Desktop")

    file_dialog: tuple[str, ...] | str = askopenfilenames(
        filetypes=filetypes,
        initialdir=initialdir,
        title=ask_directory_title)

    logger.info(f"Файлы: {file_dialog}")

    return file_dialog if isinstance(file_dialog, tuple) else None


class TextValue(NamedTuple):
    text: str
    value: int

    @classmethod
    def document_element(cls, name: str):
        _dict: tuple[tuple[str, int], ...] = document_text_value.get(name)

        return tuple(cls(k, v) for k, v in _dict)

    def __repr__(self):
        return f"{self.text} -> {self.value}"

    __str__ = __repr__
