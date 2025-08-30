# -*- coding: utf-8 -*-

from pathlib import Path
from sys import platform

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QKeyEvent, QCloseEvent
from PySide6.QtWidgets import QDialog, QRadioButton, QGroupBox, QCheckBox, QApplication, \
    QDialogButtonBox, QMessageBox, QFileDialog, QPushButton, QSizePolicy, QLayout, QHBoxLayout
from loguru import logger

from docx_modify.enum_element import UserInputValues, DocumentSide, DocumentMode
from docx_modify.exceptions import WidgetNotFoundError
from docx_modify.interface.constants import DirectionLayout, WidgetAttrs, Geometry, InputAttribute


def specify_group_box(group_box: QGroupBox, direction: DirectionLayout, attributes: WidgetAttrs):
    group_box.setLayout(direction.layout())
    group_box.setObjectName(attributes.name)
    group_box.setGeometry(attributes.geometry.to_qrect())
    group_box.setFont(attributes.font)
    group_box.setTitle(attributes.text)
    group_box.setMinimumSize(attributes.geometry.size())
    group_box.setMaximumSize(attributes.geometry.size())
    group_box.setFixedSize(attributes.geometry.size())
    group_box.setAlignment(Qt.AlignmentFlag.AlignLeft)
    group_box.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)


def specify_widget(widget: QRadioButton | QCheckBox, group_box: QGroupBox, attributes: WidgetAttrs):
    widget.setObjectName(attributes.name)
    widget.setGeometry(attributes.geometry.to_qrect())
    widget.setFont(attributes.font)
    widget.setText(attributes.text)
    widget.setMinimumSize(attributes.geometry.size())
    widget.setMaximumSize(attributes.geometry.size())
    widget.setFixedSize(attributes.geometry.size())
    widget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
    widget.setParent(group_box)


def get_pressed_button(group_box: QGroupBox):
    dict_group_box: dict[str, str] = {
        "mode": "Вид",
        "side": "Форматирование"}

    button: QRadioButton | QCheckBox

    for button in group_box.children():
        if isinstance(button, QRadioButton) and button.isChecked():
            return button.objectName()

    else:
        logger.warning(f"Ни одна из кнопок в группе {dict_group_box.get(group_box.objectName())} не выбрана")


def generate_warning_window(rb_group: str):
    message_box: QMessageBox = QMessageBox()
    message_box.setIcon(QMessageBox.Icon.Warning)
    message_box.setText(f"Не выбрана ни одна опция в секции {rb_group}")
    message_box.setWindowTitle("Ошибка при выборе опций")
    message_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    message_box.buttonClicked.connect(message_box.accept)
    message_box.exec()


def generate_file_dialog() -> list[str] | None:
    path_files, _ = QFileDialog.getOpenFileNames(
        caption="Выберите один или несколько файлов для обработки:",
        dir=Path.home().joinpath("Desktop").as_posix(),
        filter="doc files (*.docx *.docm);;docx files (*.docx);;docm files (*.docm)")
    return path_files


class DialogWindow(QDialog):
    base_font_size: int = 8 if platform.startswith("win") else 14

    group_font: QFont = QFont(
        "PT Sans",
        base_font_size,
        QFont.Weight.Normal,
        False)
    selectable_font: QFont = QFont(
        "PT Sans",
        base_font_size + 2,
        QFont.Weight.Bold,
        False)
    label_font: QFont = QFont(
        "PT Sans",
        base_font_size + 4,
        QFont.Weight.Bold,
        False)

    dict_side: dict[str, DocumentSide] = {
        "single": DocumentSide.SINGLE,
        "mirror": DocumentSide.MIRROR}

    dialog_attributes: WidgetAttrs = WidgetAttrs(
        "mainDialog",
        Geometry(0, 0, 730, 360),
        label_font,
        "Конвертация файлов")

    def __init__(self, user_input_values: UserInputValues):
        super().__init__()

        self._widgets: dict[str, QRadioButton | QCheckBox | QGroupBox | QDialogButtonBox] = dict()
        self._user_input_values: UserInputValues = user_input_values
        self.setWindowFlag(Qt.WindowType.WindowTitleHint, False)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setMinimumSize(self.dialog_attributes.geometry.size())
        self.setMaximumSize(self.dialog_attributes.geometry.size())
        self.setFixedSize(self.dialog_attributes.geometry.size())

    def set_button_box(self):
        button_box_attributes: WidgetAttrs = WidgetAttrs(
            "button_box",
            Geometry(180, 310, 340, 30),
            self.selectable_font,
            None)

        button_box: QDialogButtonBox = QDialogButtonBox(parent=self)

        button_box.setObjectName("button_box")
        button_box.setGeometry(button_box_attributes.geometry.to_qrect())
        button_box.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        button_box.setMinimumSize(button_box_attributes.geometry.size())
        button_box.setMaximumSize(button_box_attributes.geometry.size())
        button_box.setFixedSize(button_box_attributes.geometry.size())
        button_box.setParent(self)
        button_box.accepted.connect(self.ok)
        button_box.rejected.connect(lambda: self.cancel("Работа прервана по нажатии на кнопку Отмена"))

        ok_geometry: Geometry = Geometry(500, 320, 100, 30)

        ok: QPushButton = QPushButton(parent=button_box)

        ok.setText("ОК")
        ok.setFont(self.selectable_font)
        ok.setGeometry(ok_geometry.to_qrect())
        ok.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        ok.setMinimumSize(ok_geometry.size())
        ok.setMaximumSize(ok_geometry.size())
        ok.setFixedSize(ok_geometry.size())
        ok.setAutoFillBackground(True)

        cancel_geometry: Geometry = Geometry(600, 320, 100, 30)

        cancel: QPushButton = QPushButton(parent=button_box)

        cancel.setText("Отмена")
        cancel.setFont(self.selectable_font)
        cancel.setGeometry(cancel_geometry.to_qrect())
        cancel.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        cancel.setMinimumSize(cancel_geometry.size())
        cancel.setMaximumSize(cancel_geometry.size())
        cancel.setFixedSize(cancel_geometry.size())
        cancel.setAutoFillBackground(True)

        button_box.addButton(ok, QDialogButtonBox.ButtonRole.AcceptRole)
        button_box.addButton(cancel, QDialogButtonBox.ButtonRole.RejectRole)

        button_box.show()
        self._widgets["button_box"] = button_box

    def check_pressed(self, group_box: str):
        return get_pressed_button(self[group_box]) is not None

    def ok(self):
        if self.get("typo").isChecked():
            self.accept()

        elif not self.check_pressed("mode"):
            generate_warning_window("Вид")

        elif not self.get("typo").isChecked() and not self.check_pressed("side"):
            generate_warning_window("Форматирование")

        else:
            if self.get("prog").isChecked():
                document_mode: DocumentMode = DocumentMode.PROG
                def_ministry: bool = False

            else:
                document_mode: DocumentMode = DocumentMode.ARCH
                def_ministry: bool = self.get("def_ministry").isChecked()

            side: str = get_pressed_button(self.get("side"))
            document_side: DocumentSide = self.dict_side.get(side)

            change_list: bool = self.get("change_list").isChecked()
            approvement_list: bool = self.get("approvement_list").isChecked()

            kwargs: dict[str, DocumentMode | DocumentSide | bool] = {
                "document_mode": document_mode,
                "document_side": document_side,
                "change_list": change_list,
                "def_ministry": def_ministry,
                "approvement_list": approvement_list}

            self._user_input_values.specify(**kwargs)

            self.accept()

    def specify(self):
        self.setObjectName(self.dialog_attributes.name)
        self.setGeometry(self.dialog_attributes.geometry.to_qrect())
        self.setFont(self.dialog_attributes.font)
        self.setWindowTitle(self.dialog_attributes.text)
        self.setMinimumSize(self.dialog_attributes.geometry.size())
        self.setMaximumSize(self.dialog_attributes.geometry.size())
        self.setFixedSize(self.dialog_attributes.geometry.size())
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def __add__(self, other):
        if isinstance(other, (QRadioButton, QCheckBox, QGroupBox)):
            self._widgets[other.objectName()] = other

        else:
            return NotImplemented

    def __getitem__(self, item):
        if isinstance(item, str):
            return self._widgets.get(item)

        else:
            logger.info(f"Виджет {item} не найден")
            raise WidgetNotFoundError

    def get(self, item):
        return self.__getitem__(item)

    def __setitem__(self, key, value):
        if isinstance(key, str) and isinstance(value, (QRadioButton, QCheckBox, QGroupBox)):
            self._widgets[key] = value

        else:
            logger.info(
                f"Ключ {key} должен быть типа str, а значение {value} -- типа QRadioButton, QCheckBox, QGroupBox, "
                f"но получено {type(key)} и {type(value)}")
            raise TypeError

    def set_group_box(self, direction: DirectionLayout, widget_attrs: WidgetAttrs) -> QGroupBox:
        group_box: QGroupBox = QGroupBox(parent=self)

        specify_group_box(group_box, direction, widget_attrs)
        self + group_box
        group_box.show()
        return group_box

    def set_rb(self, group_box: QGroupBox, widget_attrs: WidgetAttrs) -> QRadioButton:
        rb: QRadioButton = QRadioButton(parent=group_box)

        specify_widget(rb, group_box, widget_attrs)
        rb.autoExclusive()
        self + rb
        rb.show()
        return rb

    def set_cb(self, group_box: QGroupBox, attributes: WidgetAttrs) -> QCheckBox:
        cb: QCheckBox = QCheckBox(parent=group_box)

        specify_widget(cb, group_box, attributes)
        self + cb
        cb.show()
        return cb

    def set_mode_rb(self):
        self.get("arch").toggled.connect(self.arch_command)
        self.get("typo").toggled.connect(self.typo_command)
        self.get("prog").toggled.connect(self.prog_command)

    def typo_command(self):
        self.get("side").setEnabled(False)
        self.get("cb_group").setEnabled(False)

    def arch_command(self):
        self.get("side").setEnabled(True)
        self.get("cb_group").setEnabled(True)
        self.get("def_ministry").setEnabled(True)

    def prog_command(self):
        self.get("side").setEnabled(True)
        self.get("cb_group").setEnabled(True)
        self.get("def_ministry").setEnabled(False)

    def run(self):
        self.specify()
        self.set_button_box()

        mode_attributes: WidgetAttrs = WidgetAttrs(
            "mode",
            Geometry(20, 20, 690, 80),
            self.group_font,
            "Вид")
        arch_attributes: WidgetAttrs = WidgetAttrs(
            "arch",
            Geometry(10, 35, 190, 30),
            self.selectable_font,
            "Архивный",
            InputAttribute.DOCUMENT_MODE,
            DocumentMode.ARCH)
        typo_attributes: WidgetAttrs = WidgetAttrs(
            "typo",
            Geometry(250, 35, 190, 30),
            self.selectable_font,
            "Типографский",
            InputAttribute.DOCUMENT_MODE,
            DocumentMode.TYPO)
        prog_attributes: WidgetAttrs = WidgetAttrs(
            "prog",
            Geometry(490, 35, 190, 30),
            self.selectable_font,
            "Программный",
            InputAttribute.DOCUMENT_MODE,
            DocumentMode.PROG)

        bg_mode: QGroupBox = self.set_group_box(DirectionLayout.H, mode_attributes)
        arch: QRadioButton = self.set_rb(bg_mode, arch_attributes)
        typo: QRadioButton = self.set_rb(bg_mode, typo_attributes)
        prog: QRadioButton = self.set_rb(bg_mode, prog_attributes)

        mode_layout: QHBoxLayout | QLayout = bg_mode.layout()
        mode_layout.addWidget(arch)
        mode_layout.addSpacing(50)
        mode_layout.addWidget(typo)
        mode_layout.addSpacing(50)
        mode_layout.addWidget(prog)

        side_attributes: WidgetAttrs = WidgetAttrs(
            "side",
            Geometry(20, 100, 690, 80),
            self.group_font,
            "Форматирование")

        single_attributes: WidgetAttrs = WidgetAttrs(
            "single",
            Geometry(10, 35, 190, 30),
            self.selectable_font,
            "Односторонняя печать",
            InputAttribute.DOCUMENT_SIDE,
            DocumentSide.SINGLE)
        mirror_attributes: WidgetAttrs = WidgetAttrs(
            "mirror",
            Geometry(250, 35, 190, 30),
            self.selectable_font,
            "Двусторонняя печать",
            InputAttribute.DOCUMENT_SIDE,
            DocumentSide.MIRROR)

        bg_side: QGroupBox = self.set_group_box(DirectionLayout.H, side_attributes)
        single: QRadioButton = self.set_rb(bg_side, single_attributes)
        mirror: QRadioButton = self.set_rb(bg_side, mirror_attributes)

        side_layout: QHBoxLayout | QLayout = bg_side.layout()
        side_layout.addWidget(single)
        side_layout.addSpacing(60)
        side_layout.addWidget(mirror)
        side_layout.addSpacing(60)
        side_layout.insertStretch(-1)

        cb_attributes: WidgetAttrs = WidgetAttrs(
            "cb_group",
            Geometry(20, 180, 690, 130),
            self.group_font,
            None)
        change_list_attributes: WidgetAttrs = WidgetAttrs(
            "change_list",
            Geometry(10, 50, 480, 30),
            self.selectable_font,
            "Добавить Лист регистрации изменений в конец документа?",
            InputAttribute.CHANGE_LIST,
            True)
        def_ministry_attributes: WidgetAttrs = WidgetAttrs(
            "def_ministry",
            Geometry(10, 10, 480, 30),
            self.selectable_font,
            "Поставка для Министерства Обороны РФ?",
            InputAttribute.DEF_MINISTRY,
            True)
        approvement_list_attributes: WidgetAttrs = WidgetAttrs(
            "approvement_list",
            Geometry(10, 90, 480, 30),
            self.selectable_font,
            "Добавить штамп Листа утверждения на титульный лист?",
            InputAttribute.APPROVEMENT_LIST,
            True)

        group_box: QGroupBox = self.set_group_box(DirectionLayout.V, cb_attributes)
        def_ministry: QCheckBox = self.set_cb(group_box, def_ministry_attributes)
        change_list: QCheckBox = self.set_cb(group_box, change_list_attributes)
        approvement_list: QCheckBox = self.set_cb(group_box, approvement_list_attributes)

        group_box.layout().addWidget(def_ministry)
        group_box.layout().addWidget(change_list)
        group_box.layout().addWidget(approvement_list)

        self.set_mode_rb()

        self.setVisible(True)
        self.show()

    def cancel(self, message: str):
        logger.error(message)
        super().close()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            logger.error("Работа прервана по нажатии на клавишу <ESC>")
            super().close()

        else:
            super().keyPressEvent(event)

    def closeEvent(self, event: QCloseEvent):
        self._user_input_values.disable()
        event.accept()

    @property
    def user_input_values(self):
        return self._user_input_values


def get_user_input():
    user_input_values: UserInputValues = UserInputValues()

    if QApplication.instance():
        QApplication.instance().shutdown()

    app: QApplication = QApplication()

    path_files: list[str] | None = generate_file_dialog()

    if path_files is None or path_files == []:
        app.quit()
        logger.error("Работа программы завершена пользователем")
        user_input_values.disable()

    else:
        user_input_values.path_files = path_files

        app_gui: DialogWindow = DialogWindow(user_input_values)
        app_gui.run()

        app.exec()

        if app_gui.user_input_values.is_none:
            app_gui._user_input_values = None

        user_input_values: UserInputValues = app_gui.user_input_values
        app.quit()
        logger.info(f"user_input_values = {user_input_values!r}")

    return user_input_values


if __name__ == '__main__':
    get_user_input()
