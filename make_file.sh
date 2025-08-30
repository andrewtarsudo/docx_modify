#!/bin/sh

cd ./docx_modify || (echo "Directory docx_modify is not found" && exit 1)

if [[ "${OSTYPE}" == "msys"* ]]; then
  pyinstaller --noconfirm --distpath "../bin" "docx_modify.exe.spec"
elif [[ "${OSTYPE}" == "linux"* || "${OSTYPE}" == "darwin"* ]]; then
  pyinstaller --noconfirm --distpath "../bin" "docx_modify.spec"
fi

exit 0