# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2023 Advanced Micro Devices, Inc.

message("----CMAKE_CURRENT_BINARY_DIR=${CMAKE_CURRENT_BINARY_DIR}")
message("----CMAKE_INSTALL_PREFIX=${CMAKE_INSTALL_PREFIX}")
message("----CMAKE_BINARY_DIR=${CMAKE_BINARY_DIR}")
message("----PROJECT_BINARY_DIR=${PROJECT_BINARY_DIR}")
message("----PY_ELFLIB_INSTALL_DIR=${PY_ELFLIB_INSTALL_DIR}")
message("----PY_ELFLIB_BUILD_INSTALL_DIR=${PY_ELFLIB_BUILD_INSTALL_DIR}")

add_test(NAME libelf-classic
  COMMAND "${PROJECT_SOURCE_DIR}/test/libelf-classic.py" "libelf-classic.out"
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})

add_test(NAME multiple-sections
  COMMAND "${PROJECT_SOURCE_DIR}/test/multiple-sections.py" "multiple-sections.out"
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})

add_test(NAME strtab
  COMMAND "${PROJECT_SOURCE_DIR}/test/strtab.py" "strtab.out"
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})

set_tests_properties(libelf-classic multiple-sections strtab PROPERTIES ENVIRONMENT
  "PYTHONPATH=${PY_ELFLIB_BUILD_INSTALL_DIR}")
