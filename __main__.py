# -*- coding: utf-8 -*-
from sys import version_info
from warnings import filterwarnings

from docx_modify.const import log_folder
from docx_modify.exceptions import InvalidPythonVersion


def main():
    filterwarnings("ignore")

    if version_info < (3, 8):
        print("Версия Python должна быть не менее 3.8")
        input("Нажмите <Enter>, чтобы закрыть окно ...")
        raise InvalidPythonVersion

    if not log_folder.exists():
        log_folder.mkdir(parents=True, exist_ok=True)

    try:
        from docx_modify.file_processing import run_script

        run_script()

    except ModuleNotFoundError as e:
        print("Если запускается на macOS, Tk устанавливается с помощью команды \nbrew install python-tk")
        print(f"Ошибка портирования модуля {e.name}: {e.msg}")
        input()


if __name__ == '__main__':
    main()
