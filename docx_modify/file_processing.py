# -*- coding: utf-8 -*-
from pathlib import Path
from shutil import rmtree
from textwrap import dedent
from time import sleep

from loguru import logger

from docx_modify.const import temp_path, log_folder
from docx_modify.core_elements.core_document import CoreDocument
from docx_modify.core_elements.core_zip_file import CoreZipFile
from docx_modify.enum_element import DocumentMode, DocumentSide, FileItem, SectionOrientation, UserInputValues, \
    CompanyName
from docx_modify.exceptions import BaseError
from docx_modify.interface.gui import get_user_input
from docx_modify.init_logger import custom_logging
from docx_modify.word_elements.word_file_collection import WordFileCollection
from docx_modify.xml_elements.xml_body import XmlBody
from docx_modify.xml_elements.xml_content_types import XmlContentTypes
from docx_modify.xml_elements.xml_document import XmlDocument
from docx_modify.xml_elements.xml_file_fixer import XmlFileFixer
from docx_modify.xml_elements.xml_hdr_ftr import HdrFtrReference, HdrFtrRelReferenceController
from docx_modify.xml_elements.xml_properties import XmlProperties, DocProperty
from docx_modify.xml_elements.xml_relationships import XmlRelationship, XmlRelationshipsGlobal, XmlWordRelationships
from docx_modify.xml_elements.xml_section import XmlSection
from docx_modify.xml_elements.xml_settings import XmlSettings
from docx_modify.xml_elements.xml_styles import XmlChangeListStyles, XmlBasicStyles


def show_prompt():
    """Specifies and outputs the prompt in the console."""
    _help: str = dedent("""\
-------------------------------------------------------------------------------
В любом из окон:

* Для подтверждения выбора нажмите кнопку Ok.
* Для прекращения работы скрипта нажмите кнопку Отмена, Закрыть в верхнем углу меню или клавишу <Esc>.

Краткий алгоритм:

1. В открывшемся окне выберите файлы, которые необходимо изменить.

** Можно указать сразу несколько файлов. **

2. В открывшемся окне укажите вид файла: архивный (с рамкой по ГОСТ), типографский или программный.

В архивном виде к файлу добавляется рамка, установленная ГОСТ.
В типографском виде в файле присутствуют только верхние и нижние колонтитулы.
В программном виде к файлу добавляются номер страницы и децимальный номер в верхний колонтитул 
и таблицу изменений снизу. 

3. Если вид архивный или программный, то укажите форматирование файлов: для односторонней или двусторонней печати.

При форматировании для двусторонней печати рамки на обеих сторонах листа совпадают.
При форматировании для односторонней печати рамки на всех страницах имеют одинаковые отступы.

4. Если вид архивный, то выберите, нужно ли оформление привести к требованиям МО РФ.

При активации к нижней рамке на 2 листе добавляются дополнительные ячейки.

5. Если вид архивный или программный, то выберите, нужно ли добавить Лист регистрации изменений в конец документа.

При активации в документ вставляется таблица для Листа регистрации изменений вместе с заголовком.

6. Если вид архивный или программный, то выберите, нужно ли добавить информацию о Листе утверждения 
на титульную страницу.

При активации в верхний колонтитул добавляются строки:

УТВЕРЖДЕН
<Децимальный номер><Сокращение типа документа>-ЛУ

В терминах свойств документа:

УТВЕРЖДЕН
{DOCPROPERTY _DecimalNum_}{DOCPROPERTY _DocTypeShort_}-ЛУ

7. По завершении работы программы нажмите клавишу <Enter>, чтобы закрыть панель.

8. В обработанном документе обновите все поля со значением "ОБНОВИТЬ".

9. В обработанном документе заполните необходимые пустые поля.
-------------------------------------------------------------------------------""")
    print(_help)
    sleep(1)


def _core_preprocessing(path: Path, document_mode: DocumentMode) -> CoreZipFile:
    _names: dict[DocumentMode, str] = {
        DocumentMode.ARCH: "арх",
        DocumentMode.TYPO: "тпг",
        DocumentMode.PROG: "прг"}

    core_document: CoreDocument = CoreDocument(path)
    core_document.duplicate(_names.get(document_mode))
    core_zip_file: CoreZipFile = CoreZipFile(core_document)
    core_zip_file.unarchive()
    logger.success(f"Разархивирован файл {path}")

    return core_zip_file


def _delete_files(core_zip_file: CoreZipFile):
    core_zip_file.delete_files("word/header*.xml")
    core_zip_file.delete_files("word/footer*.xml")
    core_zip_file.delete_files("word/_rels/header*.xml.rels")
    core_zip_file.delete_files("word/_rels/footer*.xml.rels")

    logger.success("Удалены старые колонтитулы")


def _word_files_processing(
        core_zip_file: CoreZipFile,
        document_mode: DocumentMode,
        company_name: CompanyName,
        def_ministry: bool):
    word_file_collection: WordFileCollection
    word_file_collection = WordFileCollection(core_zip_file, document_mode, company_name, def_ministry)
    word_file_collection.add_word_files()
    word_file_collection.add_word_file_image()

    word_file_collection.add_to_archive("headers_footers")

    logger.success("Добавлены новые колонтитулы")

    word_file_collection.add_to_archive("rels")
    word_file_collection.add_to_archive("image")

    logger.success("Добавлен логотип")

    word_file_collection.add_word_file_military()


def _xml_files_processing(
        core_zip_file: CoreZipFile,
        document_side: DocumentSide,
        document_mode: DocumentMode):
    xml_settings: XmlSettings = XmlSettings(core_zip_file, document_side, document_mode)
    xml_settings.read()
    xml_settings.set_settings()

    logger.success("Изменены параметры файла")


def _xml_styles_processing(core_zip_file: CoreZipFile, change_list: bool):
    xml_basic_styles: XmlBasicStyles = XmlBasicStyles(core_zip_file)
    xml_basic_styles.read()
    xml_basic_styles.add_styles()

    if change_list:
        xml_change_list_styles: XmlChangeListStyles = XmlChangeListStyles(core_zip_file)
        xml_change_list_styles.add_styles()

    logger.success("Добавлены новые стили")


def _xml_content_types_processing(core_zip_file: CoreZipFile, document_mode: DocumentMode):
    xml_content_types: XmlContentTypes = XmlContentTypes(core_zip_file, document_mode)
    xml_content_types.read()
    xml_content_types.fix_content_types()

    logger.success("Обновлен файл [Content_Types].xml")


def _xml_properties_processing(core_zip_file: CoreZipFile, document_side: DocumentSide, company_name: CompanyName):
    xml_properties: XmlProperties = XmlProperties(core_zip_file, document_side)
    xml_properties.read()
    xml_properties.set_properties(company_name)

    logger.success("Определены пользовательские свойства документа")

    if not xml_properties.exists:
        xml_relationships: XmlRelationshipsGlobal = XmlRelationshipsGlobal(core_zip_file)
        xml_relationships.read()
        xml_relationships.set_xml_relationships()
        xml_relationships.add_custom()


def _get_company_name(core_zip_file: CoreZipFile, document_side: DocumentSide):
    xml_properties: XmlProperties = XmlProperties(core_zip_file, document_side)
    xml_properties.read()

    doc_property: DocProperty | None = xml_properties.get_property("_DecimalNum_")
    decimal_number: str | None = doc_property.lpwstr if isinstance(doc_property, DocProperty) else None

    return CompanyName.from_decimal_number(decimal_number)


def _xml_relationships_file(core_zip_file: CoreZipFile) -> XmlWordRelationships:
    xml_relationships: XmlWordRelationships = XmlWordRelationships(core_zip_file)
    xml_relationships.read()
    xml_relationships.set_xml_relationships()
    xml_relationships.delete_rels(xml_relationships.hdr_ftr_references().values())
    xml_relationships.save()

    logger.success("Изменены внутренние ссылки")

    return xml_relationships


def _hdr_ftr_rel_references(
        xml_relationships: XmlWordRelationships,
        document_mode: DocumentMode,
        def_ministry: bool) -> HdrFtrRelReferenceController:
    _hdr_ftr: HdrFtrRelReferenceController = HdrFtrRelReferenceController(
        document_mode=document_mode,
        def_ministry=def_ministry).make_hdr_ftr_rel_ref_mode()
    _hdr_ftr.generate_all()

    for k, v in _hdr_ftr.rel_target_rel_type.items():
        rel_id: str = f"{xml_relationships.next_rel_id()}"
        xml_relationship: XmlRelationship = XmlRelationship(rel_id, v, k, xml_relationships)
        xml_relationships.add_xml_relationship(xml_relationship)

    xml_relationships.save()
    xml_rels: str = "\n".join([f"ключ {k}, значение {v}" for k, v in xml_relationships.items()])

    logger.info(f"Relationships:\n{xml_rels}")

    return _hdr_ftr


def _xml_document_file(
        core_zip_file: CoreZipFile,
        document_mode: DocumentMode,
        document_side: DocumentSide,
        change_list: bool,
        xml_relationships: XmlWordRelationships,
        hdr_ftr: HdrFtrRelReferenceController):
    xml_document: XmlDocument = XmlDocument(core_zip_file)
    xml_document.read()

    for section_index in range(len(xml_document)):
        xml_section: XmlSection = XmlSection(
            xml_document, section_index, document_mode, document_side).make_xml_section_mode()
        xml_section.read()
        xml_section.set_section()

        if xml_section.orientation == SectionOrientation.LANDSCAPE:
            _section_index: int = -1

        elif section_index > 2:
            _section_index: int = 2

        else:
            _section_index: int = section_index

        for header_footer in hdr_ftr.section_hdr_ftr(_section_index):
            rel_id: str = xml_relationships.hdr_ftr_references().get(header_footer.rel_target.value)
            hdr_ftr_reference: HdrFtrReference = header_footer.hdr_ftr_reference(rel_id)

            xml_section.add_header_footer_reference(hdr_ftr_reference)
            xml_section.write()

    logger.success("Изменены секции в файле")

    if change_list:
        xml_body: XmlBody = XmlBody(xml_document)
        xml_body.set_change_list()
        logger.success("Добавлен лист регистрации изменений")
    # close the file
    xml_document.save()


def _xml_file_fix(
        document_mode: DocumentMode,
        document_side: DocumentSide,
        approvement_list: bool):
    xml_file_fixer: XmlFileFixer = XmlFileFixer(
        document_mode=document_mode,
        document_side=document_side,
        approvement_list=approvement_list)
    xml_file_fixer.replace()


def file_modify(file_item: FileItem):
    rmtree(temp_path.joinpath("_docx_temp"), True)

    logger.info("Временная директория _docx_temp удалена")

    # initiate the core files and classes, unpack the docx document as the ZIP archive
    core_zip_file: CoreZipFile = _core_preprocessing(file_item.path_file, file_item.document_mode)
    _str_files: str = "\n".join(core_zip_file.files)
    logger.info(f"Файлы внутри архива:\n{_str_files}")

    with core_zip_file as core_zf:
        _delete_files(core_zf)

        company_name: CompanyName = _get_company_name(core_zf, file_item.document_side)

        _xml_properties_processing(core_zf, file_item.document_side, company_name)

        # do operations with the xml files without parsing them
        _word_files_processing(core_zf, file_item.document_mode, company_name, file_item.def_ministry)

        # do some changes in the xml files based on the predefined ones
        _xml_content_types_processing(core_zf, file_item.document_mode)
        _xml_files_processing(core_zf, file_item.document_side, file_item.document_mode)
        _xml_styles_processing(core_zf, file_item.change_list)

        # do some changes in the document.xml.rels file
        xml_relationships: XmlWordRelationships = _xml_relationships_file(core_zf)
        xml_relationships.read()

        # do operations with the header*.xml and footer*.xml files
        hdr_ftr_rel_controller: HdrFtrRelReferenceController = _hdr_ftr_rel_references(
            xml_relationships,
            file_item.document_mode,
            file_item.def_ministry)

        # do operations with the sectPr and headerReference/footerReference elements
        _xml_document_file(
            core_zf,
            file_item.document_mode,
            file_item.document_side,
            file_item.change_list,
            xml_relationships,
            hdr_ftr_rel_controller)

        # fill in the gaps in the xml files
        _xml_file_fix(file_item.document_mode, file_item.document_side, file_item.approvement_list)

        # pack the archive to the docx file
        core_zf.delete_temp_archive()

    logger.success("Файл сохранен")
    logger.success(f'Обработка файла "{file_item.path_file}" завершена')
    logger.success(f"Новый файл: {core_zip_file.name_updated()}")
    print("-------------------------------------------------------------------------------\n")
    return


@logger.catch
def run_script():
    """Main entrance point of the program."""
    custom_logging("docx_modify")
    _error_flag: bool = False

    show_prompt()
    user_input_values: UserInputValues | None = get_user_input()

    if user_input_values is not None:
        for file_item in iter(user_input_values):
            try:
                file_modify(file_item)

            except PermissionError as e:
                logger.error(f"Недостаточно прав для изменения файла {e.strerror}")
                _error_flag = True
                continue

            except RuntimeError:
                logger.error(f"Ошибка обработки файла {file_item.path_file}")
                _error_flag = True
                continue

            except FileNotFoundError as e:
                logger.error(f"Не найден файл {e.filename}")
                _error_flag = True
                continue

            except BaseError as e:
                logger.error(f"Возникла ошибка {e.__class__.__name__}.\n{str(e)}")
                _error_flag = True
                continue

            except OSError as e:
                logger.error(f"Ошибка {e.__class__.__name__}.\n{e.strerror}")
                _error_flag = True
                continue

    logger.remove()

    if not _error_flag:
        rmtree(log_folder, True)

    else:
        print(f"Лог-файл находится в директории {log_folder}")

    input("Нажмите клавишу <Enter>, чтобы закрыть окно ...")
