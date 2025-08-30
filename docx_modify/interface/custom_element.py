# -*- coding: utf-8 -*-
from tkinter import IntVar, Misc
from tkinter.constants import FLAT
from tkinter.ttk import Button, Frame, Radiobutton, Checkbutton
from typing import Callable

from loguru import logger

from docx_modify.interface.constants import TextValue, null_command, def_ministry_title, change_list_title, \
    approvement_list_title, button_names, frame_radiobutton_geometry, place_radiobutton_left, \
    place_radiobutton_center, frame_checkbutton_geometry, place_change_list, place_def_ministry, \
    place_approvement_list, frame_button_geometry, checkbutton_geometry, place_ok, place_cancel, \
    place_radiobutton_right


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

    def __init__(
            self,
            frame: Frame,
            command: Callable,
            name: str, *,
            width: int = None,
            height: int = None):
        kwargs: dict[str, int] = {}

        if height is not None and height >= 0:
            kwargs["height"] = height

        if width is not None and width >= 0:
            kwargs["width"] = width

        super().__init__(
            frame,
            command=command,
            default="normal",
            name=name,
            style="b.TButton",
            text=button_names.get(name),
            **kwargs)
        self.is_shown: bool | None = True

    @classmethod
    def ok_button(cls, frame: Frame, command: Callable):
        return cls(frame, command, "ok")

    @classmethod
    def cancel_button(cls, frame: Frame, command: Callable):
        return cls(frame, command, "cancel")

    def __bool__(self):
        return self.is_shown


class CustomRadiobutton(Radiobutton):
    def __init__(
            self,
            frame: Frame,
            name: str, *,
            text_value: TextValue,
            variable: IntVar,
            command: Callable = None,
            width: int = None,
            height: int = None):
        kwargs: dict[str, int] = {}

        if height is not None and height >= 0:
            kwargs["height"] = height

        if width is not None and width >= 0:
            kwargs["width"] = width

        if command is None:
            command: Callable = null_command

        super().__init__(
            frame,
            command=command,
            text=text_value.text,
            variable=variable,
            value=text_value.value,
            style="rb.TRadiobutton",
            **kwargs)
        self._name: str = name
        self.is_shown: bool | None = True

    @classmethod
    def document_mode_arch(cls, frame: Frame, variable: IntVar, command: Callable = None):
        text_value: TextValue = TextValue.document_element("document_mode")[1]

        return cls(
            frame,
            "arch",
            text_value=text_value,
            variable=variable,
            command=command)

    @classmethod
    def document_mode_typo(cls, frame: Frame, variable: IntVar, command: Callable = None):
        text_value: TextValue = TextValue.document_element("document_mode")[0]

        return cls(
            frame,
            "typo",
            text_value=text_value,
            variable=variable,
            command=command)

    @classmethod
    def document_mode_prog(cls, frame: Frame, variable: IntVar, command: Callable = None):
        text_value: TextValue = TextValue.document_element("document_mode")[2]

        return cls(
            frame,
            "prog",
            text_value=text_value,
            variable=variable,
            command=command)

    @classmethod
    def document_side_single(cls, frame: Frame, variable: IntVar):
        text_value: TextValue = TextValue.document_element("document_side")[0]

        return cls(
            frame,
            "single",
            text_value=text_value,
            variable=variable)

    @classmethod
    def document_side_mirror(cls, frame: Frame, variable: IntVar):
        text_value: TextValue = TextValue.document_element("document_side")[1]

        return cls(
            frame,
            "mirror",
            text_value=text_value,
            variable=variable)

    @property
    def name(self):
        return self._name


class CustomCheckbutton(Checkbutton):
    def __init__(
            self,
            frame: Frame,
            name: str, *,
            text: str,
            variable: IntVar,
            width: int = None,
            height: int = None):
        kwargs: dict[str, int] = {}

        if height is not None and height > 0:
            kwargs["height"] = height

        if width is not None and width >= 0:
            kwargs["width"] = width

        super().__init__(
            frame,
            command=null_command,
            text=text,
            variable=variable,
            onvalue=True,
            offvalue=False,
            style="cb.TCheckbutton",
            **kwargs)
        self._name: str = name
        self.is_shown: bool | None = True

    @classmethod
    def def_ministry(cls, frame: Frame, variable: IntVar):
        return cls(
            frame,
            "def_ministry",
            text=def_ministry_title,
            variable=variable,
            **checkbutton_geometry)

    @classmethod
    def change_list(cls, frame: Frame, variable: IntVar):
        return cls(
            frame,
            "change_list",
            text=change_list_title,
            variable=variable,
            **checkbutton_geometry)

    @classmethod
    def approvement_list(cls, frame: Frame, variable: IntVar):
        return cls(
            frame,
            "approvement_list",
            text=approvement_list_title,
            variable=variable,
            **checkbutton_geometry)

    @property
    def name(self):
        return self._name


class CustomFrame(Frame):
    def __init__(
            self,
            master: Misc,
            name: str,
            width: int = None,
            height: int = None):
        kwargs: dict[str, int] = {}

        if height is not None and height >= 0:
            kwargs["height"] = height

        if width is not None and width >= 0:
            kwargs["width"] = width

        super().__init__(
            master,
            relief=FLAT,
            name=name,
            style="f.TFrame",
            **kwargs)

        self._widgets: dict[str, CustomCheckbutton | CustomButton | CustomRadiobutton] = {}
        self.is_shown: bool | None = True

    def __repr__(self):
        return f"{self.__class__.__name__}: {self.winfo_name()}, {self.is_shown}"

    __str__ = __repr__

    def __bool__(self):
        return self.is_shown

    def __eq__(self, other):
        if isinstance(other, Frame):
            return self.winfo_name() == other.winfo_name()

        else:
            return NotImplemented

    def __ne__(self, other):
        if isinstance(other, Frame):
            return self.winfo_name() == other.winfo_name()

        else:
            return NotImplemented

    def get_widget(self, widget: str):
        if widget not in self._widgets.keys():
            logger.info(f"Виджет Widget {widget} не найден")

        else:
            return self._widgets.get(widget)

    def full_place(self, **kwargs):
        for name, widget in self._widgets.items():
            if widget.is_shown:
                widget.pack(**kwargs.get(name))

        self.place()

    @property
    def widgets(self):
        return self._widgets


class FrameDocumentMode(CustomFrame):
    def __init__(self, master: Misc):
        super().__init__(master, "document_mode", **frame_radiobutton_geometry)

    def add_document_mode(
            self,
            variable: IntVar = None, *,
            arch_command: Callable,
            typo_command: Callable,
            prog_command: Callable):
        if variable is None:
            variable: IntVar = IntVar()

        arch_button: CustomRadiobutton = CustomRadiobutton.document_mode_arch(self, variable, arch_command)
        self._widgets[arch_button.name] = arch_button

        typo_button: CustomRadiobutton = CustomRadiobutton.document_mode_typo(self, variable, typo_command)
        self._widgets[typo_button.name] = typo_button

        prog_button: CustomRadiobutton = CustomRadiobutton.document_mode_prog(self, variable, prog_command)
        self._widgets[prog_button.name] = prog_button

    def full_place(self, **kwargs):
        self.get_widget("arch").place(**place_radiobutton_left)
        self.get_widget("typo").place(**place_radiobutton_center)
        self.get_widget("prog").place(**place_radiobutton_right)
        self.place(**kwargs)


class FrameDocumentSide(CustomFrame):
    def __init__(self, master: Misc):
        super().__init__(master, "document_side", **frame_radiobutton_geometry)

    def add_document_side(self, variable: IntVar = None):
        if variable is None:
            variable: IntVar = IntVar()

        single_button: CustomRadiobutton = CustomRadiobutton.document_side_single(self, variable)
        self._widgets[single_button.name] = single_button

        mirror_button: CustomRadiobutton = CustomRadiobutton.document_side_mirror(self, variable)
        self._widgets[mirror_button.name] = mirror_button

    def full_place(self, **kwargs):
        self.get_widget("single").place(**place_radiobutton_left)
        self.get_widget("mirror").place(**place_radiobutton_center)
        self.place(**kwargs)


class FrameCheckbuttons(CustomFrame):
    def __init__(self, master: Misc):
        super().__init__(master, "checkbuttons", **frame_checkbutton_geometry)

    def add_checkbutton(self, name: str, variable: IntVar = None):
        if variable is None:
            variable: IntVar = IntVar()

        checkbutton: CustomCheckbutton = getattr(CustomCheckbutton, name)(self, variable)
        self._widgets[checkbutton.name] = checkbutton

    def full_place(self, **kwargs):
        self.get_widget("def_ministry").place(**place_def_ministry)
        self.get_widget("change_list").place(**place_change_list)
        self.get_widget("approvement_list").place(**place_approvement_list)
        self.place(**kwargs)


class FrameOkCancel(CustomFrame):
    def __init__(self, master: Misc):
        super().__init__(master, "ok_cancel", **frame_button_geometry)

    def add_buttons(self, *, ok_command: Callable, cancel_command: Callable):
        _ok_button: CustomButton = CustomButton.ok_button(self, ok_command)
        self._widgets[_ok_button.winfo_name()] = _ok_button

        _cancel_button: CustomButton = CustomButton.cancel_button(self, cancel_command)
        self._widgets[_cancel_button.winfo_name()] = _cancel_button

    def full_place(self, **kwargs):
        self.get_widget("ok").place(**place_ok)
        self.get_widget("cancel").place(**place_cancel)
        self.place(**kwargs)
