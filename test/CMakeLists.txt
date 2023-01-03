# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2023 Advanced Micro Devices, Inc.

message("-- CMAKE_CURRENT_BINARY_DIR=${CMAKE_CURRENT_BINARY_DIR}")

file(COPY "${PROJECT_SOURCE_DIR}/.pylintrc" DESTINATION ${CMAKE_CURRENT_BINARY_DIR})

add_test(NAME libelf-classic
  COMMAND "${PROJECT_SOURCE_DIR}/test/libelf-classic.py" "libelf-classic.elf"
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})

add_test(NAME multiple-sections
  COMMAND "${PROJECT_SOURCE_DIR}/test/multiple-sections.py" "multiple-sections.elf"
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})

add_test(NAME strtab
  COMMAND "${PROJECT_SOURCE_DIR}/test/strtab.py" "strtab.elf"
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})

set_tests_properties(libelf-classic multiple-sections strtab PROPERTIES ENVIRONMENT
  "PYTHONPATH=${PY_ELFLIB_BUILD_INSTALL_DIR}")
