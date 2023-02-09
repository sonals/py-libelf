# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2023 Advanced Micro Devices, Inc.

message("-- CMAKE_CURRENT_BINARY_DIR=${CMAKE_CURRENT_BINARY_DIR}")

file(COPY "${PYLIBELF_SOURCE_DIR}/.pylintrc" DESTINATION ${CMAKE_CURRENT_BINARY_DIR})

add_test(NAME libelf-classic
  COMMAND "${PYLIBELF_SOURCE_DIR}/test/libelf-classic.py" "-o" "libelf-classic.elf" "-r"
  "${PYLIBELF_SOURCE_DIR}/test/libelf-classic.gold" WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})

add_test(NAME multiple-sections
  COMMAND "${PYLIBELF_SOURCE_DIR}/test/multiple-sections.py" "-o" "multiple-sections.elf" "-r"
  "${PYLIBELF_SOURCE_DIR}/test/multiple-sections.gold" WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})

add_test(NAME strtab
  COMMAND "${PYLIBELF_SOURCE_DIR}/test/strtab.py" "-o" "strtab.elf" "-r"
  "${PYLIBELF_SOURCE_DIR}/test/strtab.gold" WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})

set_tests_properties(libelf-classic multiple-sections strtab PROPERTIES ENVIRONMENT
  "PYTHONPATH=${PY_ELFLIB_BUILD_INSTALL_DIR}")
