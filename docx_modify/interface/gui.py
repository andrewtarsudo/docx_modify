# -*- coding: utf-8 -*-
from pathlib import Path
from sys import platform
from tkinter import Tk, IntVar, TclError, Event
from tkinter.constants import FLAT, DISABLED, ACTIVE
from tkinter.font import Font
from tkinter.ttk import Style
from typing import Literal

from loguru import logger

from docx_modify.enum_element import UserInputValues, DocumentMode, DocumentSide
from docx_modify.exceptions import InvalidOptionError
from docx_modify.interface.constants import get_files, root_title, _dict_document_side_cb, root_geometry, \
    place_document_side, place_checkbuttons, place_buttons, place_document_mode
from docx_modify.interface.custom_element import CustomFrame, FrameDocumentMode, FrameDocumentSide, FrameOkCancel, \
    FrameCheckbuttons, CustomRadiobutton, CustomButton, CustomCheckbutton


class Application:
    base_font_size: int = 14 if platform.startswith("win") else 8

    def __init__(self, root: Tk):
        self.root: Tk = root
        self.root.wm_title(root_title)
        self._user_input_values: UserInputValues | None = UserInputValues()
        self._document_mode: IntVar = IntVar()
        self._document_side: IntVar = IntVar()
        self._def_ministry: IntVar = IntVar()
        self._change_list: IntVar = IntVar()
        self._approvement_list: IntVar = IntVar()
        self._frames: dict[str, CustomFrame] = {}

        self.root.geometry(root_geometry)
        self.root.bind("<Escape>", self.exit)
        self.root.wm_resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.x_button)

        radiobutton_font: Font = Font(
            family="Times",
            name="rbf.TRadiobutton",
            size=self.base_font_size + 2,
            weight="bold",
            slant="roman",
            underline=False,
            overstrike=False)

        button_font: Font = Font(
            family="Times",
            name="bf.TButton",
            size=self.base_font_size,
            weight="normal",
            slant="roman",
            underline=False,
            overstrike=False)

        checkbutton_font: Font = Font(
            family="Times",
            name="cbf.TCheckbutton",
            size=self.base_font_size + 2,
            weight="bold",
            slant="roman",
            underline=False,
            overstrike=False)

        label_font: Font = Font(
            family="Times",
            name="lf.TLabel",
            size=self.base_font_size + 4,
            weight="bold",
            slant="roman",
            underline=False,
            overstrike=False)

        s: Style = Style(self.root)

        s.configure("l.TLabel", font=label_font)

        s.configure(
            "b.TButton",
            font=button_font,
            padx=5,
            pady=5,
            borderwidth=1,
            relief=FLAT)

        s.configure(
            "rb.TRadiobutton",
            font=radiobutton_font,
            padding=[5, 5, 5, 5],
            padx=5,
            pady=5,
            relief=FLAT)

        s.configure(
            "cb.TCheckbutton",
            font=checkbutton_font,
            padding=[5, 5, 5, 5],
            padx=5,
            pady=5,
            relief=FLAT)

        s.configure(
            "l.TLabel",
            font=label_font)

    def __getitem__(self, item):
        if isinstance(item, str):
            return self._frames.get(item)

        else:
            raise KeyError

    def get(self, item):
        return self.__getitem__(item)

    def __bool__(self):
        return bool(self.root.winfo_exists())

    def x_button(self):
        self._user_input_values = None
        logger.error("Работа прервана по нажатии на кнопку Выход")
        self.root.destroy()

    def set_state_frame(self, name: str, state: Literal["disabled", "active"]):
        try:
            frame: CustomFrame = self._frames.get(name)

            for widget_name, widget in frame.widgets.items():
                widget.configure(state=state)
                logger.debug(f"Виджет {widget_name} во фрейме {name} перешел в состояние {state}")

        except KeyError:
            logger.info(f"Фрейм {name} не найден")

    def set_state_widget(self, frame_name: str, widget_name: str, state: Literal["disabled", "active"]):
        try:
            frame: CustomFrame = self._frames.get(frame_name)

        except KeyError:
            logger.info(f"Фрейм {frame_name} не найден")

        else:
            try:
                widget: CustomCheckbutton | CustomButton | CustomRadiobutton = frame.widgets.get(widget_name)
                widget.configure(state=state)
                logger.debug(f"Виджет {widget_name} во фрейме {frame_name} перешел в состояние {state}")

            except KeyError:
                logger.info(f"Виджет {widget_name} во фрейме {frame_name} не найден")

    def add_frame(self, frame: CustomFrame, **kwargs):
        self._frames[frame.winfo_name()] = frame
        frame.full_place(**kwargs)
        self.root.update()

    def ok_command(self):
        logger.info(f"DocumentMode, нажата кнопка {self._document_mode.get()}")
        logger.info(f"DocumentSide, нажата кнопка {self._document_side.get()}")
        logger.info(f"DefMinistry, нажата кнопка {self._def_ministry.get()}")
        logger.info(f"ChangeList, нажата кнопка {self._change_list.get()}")
        logger.info(f"ApprovementList, нажата кнопка {self._approvement_list.get()}")

        # noinspection PySimplifyBooleanCheck
        if self._document_mode.get() == 0:
            self._user_input_values._document_mode = DocumentMode.TYPO
            self._user_input_values._document_side = DocumentSide.MIRROR
            self._user_input_values._def_ministry = False
            self._user_input_values._change_list = False
            self._user_input_values._approvement_list = False

        elif self._document_mode.get() == 1:
            self._user_input_values._document_mode = DocumentMode.ARCH
            self._user_input_values._document_side = _dict_document_side_cb.get(self._document_side.get(), None)
            self._user_input_values._def_ministry = bool(self._def_ministry.get())
            self._user_input_values._change_list = bool(self._change_list.get())
            self._user_input_values._approvement_list = bool(self._approvement_list.get())

        elif self._document_mode.get() == 2:
            self._user_input_values._document_mode = DocumentMode.PROG
            self._user_input_values._document_side = _dict_document_side_cb.get(self._document_side.get(), None)
            self._user_input_values._def_ministry = False
            self._user_input_values._change_list = bool(self._change_list.get())
            self._user_input_values._approvement_list = bool(self._approvement_list.get())

        else:
            logger.error(f"Некорректный выбор варианта {self._document_mode.get()}")
            raise InvalidOptionError

        self.root.destroy()

        return self._user_input_values

    def cancel_command(self):
        logger.error("Работа прервана по нажатии на кнопку Отмена")
        self._user_input_values = None
        self.root.destroy()

    def add_frame_document_mode(self):
        def typo_command():
            self.set_state_frame("document_side", DISABLED)
            self.set_state_frame("checkbuttons", DISABLED)

        def arch_command():
            self.set_state_frame("document_side", ACTIVE)
            self.set_state_frame("checkbuttons", ACTIVE)

        def prog_command():
            self.set_state_frame("document_side", ACTIVE)
            self.set_state_frame("checkbuttons", ACTIVE)
            self.set_state_widget("checkbuttons", "def_ministry", DISABLED)

        frame_document_mode: FrameDocumentMode = FrameDocumentMode(self.root)
        frame_document_mode.add_document_mode(
            self._document_mode,
            arch_command=arch_command,
            typo_command=typo_command,
            prog_command=prog_command)
        self.add_frame(frame_document_mode, **place_document_mode)

    def add_frame_document_archive(self):
        frame_document_archive: FrameDocumentSide = FrameDocumentSide(self.root)
        frame_document_archive.add_document_side(self._document_side)
        self.add_frame(frame_document_archive, **place_document_side)

    def add_frame_checkbuttons(self):
        frame_checkbuttons: FrameCheckbuttons = FrameCheckbuttons(self.root)
        frame_checkbuttons.add_checkbutton("def_ministry", self._def_ministry)
        frame_checkbuttons.add_checkbutton("change_list", self._change_list)
        frame_checkbuttons.add_checkbutton("approvement_list", self._approvement_list)
        self.add_frame(frame_checkbuttons, **place_checkbuttons)

    def add_frame_ok_cancel(self):
        frame_ok_cancel: FrameOkCancel = FrameOkCancel(self.root)
        frame_ok_cancel.add_buttons(ok_command=self.ok_command, cancel_command=self.cancel_command)
        self.add_frame(frame_ok_cancel, **place_buttons)

    def run(self):
        try:
            self.root.wm_withdraw()

            files: tuple[str, ...] | None = get_files()

            if files is None:
                self.root.destroy()

            else:
                self._user_input_values._path_files = [Path(file) for file in files]

            self.root.wm_deiconify()

            self.add_frame_document_mode()
            self.add_frame_document_archive()
            self.add_frame_checkbuttons()
            self.add_frame_ok_cancel()

            for frame in self._frames.values():
                frame.full_place()

        except TclError as e:
            logger.error("Работа программы прервана пользователем ...")
            logger.info(f"{e.__class__.__name__}, {str(e)}, {e.args}")
            self._user_input_values = None

        except InvalidOptionError:
            logger.error("Некорректная опция")
            self.root.destroy()
            self._user_input_values = None
            logger.info(self._user_input_values)

    @property
    def user_input_values(self):
        return self._user_input_values

    # noinspection PyUnusedLocal
    def exit(self, event: Event):
        self._user_input_values = None
        logger.error("Работа прервана по нажатии на клавишу <ESC>")
        self.root.destroy()


def get_user_input():
    root: Tk = Tk()
    application: Application = Application(root)
    application.run()
    application.root.mainloop()
    user_input_values: UserInputValues = application.user_input_values

    return user_input_values
