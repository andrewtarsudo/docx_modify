## Исполняемые файлы ##

### Запуск файлов ###

В директории находятся скомпилированные и упакованные исполняемые файлы. Запускаются как стандартные программы в зависимости от версии платформы:

* из GUI файловой системы:
  * Windows (`Проводник`);
  * Linux/MacOS/*nix (`Finder`);
* консоли:
  * Windows (`cmd.exe`);
  * Linux/MacOS/*nix (`Terminal`).

### Файлы для запуска программы ###

* Windows:
  * [docx_modify.exe](https://gitlab.сom/common_info/docx_modify/-/blob/097ec386baa321d6648831d19d7ba7c711b82012/bin/main.exe);
* Linux/MacOS/*nix-подобные системы:
  * [docx_modify](https://gitlab.com/common_info/docx_modify/-/blob/9b4c840b901492fa8a140263f70de9a1bf6aefad/bin/docx_modify);

**Примечание.** Возможна автозагрузка необходимого файла последней версии с помощью скрипта
`docx_modify_get_executable.py`, которая автоматически загружает последнюю версию согласно текущей платформе на рабочий стол (
`~/Desktop`) с названием `docx_modify.exe` или `docx_modify`.

Команда для запуска скрипта из командной строки:

* Windows:

```commandline
python path_to_script.py
```

* Linux/MacOS/*nix:

```commandline
python3 path_to_script.py
```