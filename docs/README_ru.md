## Файлы программы ##

* LICENSE;
* make_file.sh;
* MANIFEST.in;
* pyproject.toml;
* README.md;
* requirements.txt;
* директория `bin/`:
  * docx_modify;
  * docx_modify.exe;
  * docx_modify_get_executable.py;
  * README.md;
* директория `docx_modify/`:
  * `core_elements/`:
    * clark_name.py;
    * core_document.py;
    * updated_zip_file.py;
  * `word_elements/`:
    * word_file.py;
    * word_file_items.py;
  * `xml_elements/`:
    * xml_document.py;
    * xml_element.py;
    * xml_file.py;
    * xml_file_part.py;
    * xml_hdr_ftr.py;
    * xml_relationships.py;
    * xml_section.py;
    * xml_settings.py;
    * xml_styles.py;
  * enum_elements.py;
  * exceptions.py
  * file_processing.py;
  * init_logger.py;
  * main.py;
* директория `sources/`:
  * `headers_footers/`:
    * footer1.xml;
    * footer2.xml;
    * footer3.xml;
    * footer4.xml;
    * footer5.xml;
    * footer6.xml;
    * footer7.xml;
    * header1.xml;
    * header2.xml;
    * header3.xml;
    * header4.xml;
  * `image/`:
    * _logo_st.png;
  * `rels/`:
    * footer3.xml.rels;
  * `styles/`:
    * styles.xml;

Все используемые модули:

* стандартные Python3:
  * functools;
  * os;
  * pathlib;
  * shututil;
  * sys;
  * typing;
  * zipfile;
* сторонние:
  * loguru;
  * lxml;

### Запуск исполняемого файла ###

Путь до файла:

* Windows --- `<file_directory>.docx_modify.exe`;
* Linux/MacOS/\*nix --- `<file_directory>.docx_modify`.

Пример --- `Desktop/docx_modify.exe`/`Desktop/docx_modify`

#### Для Windows ####

1. из `Explorer`, находясь в директории `<file_directory>`;
2. из `Command Prompt`:

   1. перейти в директорию `<file_directory>` командой `cd`;

      * запустить скрипт командой `.\docx_modify.exe`; или
      * запустить скрипт командой `start docx_modify.exe`;

    ```cmd
    C:\Users\user>cd Desktop
    C:\Users\user\Desktop>.\docx_modify.exe
    C:\Users\user\Desktop>start docx_modify.exe
    ```

3. из `PowerShell`:

   * запустить скрипт командой `& "<file_directory>\docx_modify.exe"`; или
   * запустить скрипт командой `Invoke-Expression-Command "<file_directory>\docx_modify.exe"`; или
   * запустить скрипт командой `Start-Process -FilePath "<file_directory>\docx_modify.exe"`;

   ```powershell
   PS C:\Users\user> cd "C:\Users\user\Desktop\docx_modify.exe"
   PS C:\Users\user> Invoke-Expression -Command "Desktop\docx_modify.exe"
   PS C:\Users\user> Start-Process -FilePath "Desktop\docx_modify.exe" -Wait
   ```

#### Для Linux/MacOS/\*nix ####

1. из `Finder`, находясь в директории `<file_directory>`;
2. из `Terminal`/`Console`:

   * запустить скрипт командой `sh <file_directory>\docx_modify`;

   ```shell
   user@User ~ % Desktop/docx_modify
   ```