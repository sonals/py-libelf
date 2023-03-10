# SPDX-License-Identifier: MIT
# Copyright (C) 2023 Advanced Micro Devices, Inc.

message("-- CMAKE_CURRENT_BINARY_DIR=${CMAKE_CURRENT_BINARY_DIR}")

install (FILES pylibelf/elf.py DESTINATION ${PYLIBELF_BUILD_INSTALL_DIR})
install (FILES pylibelf/libelf.py DESTINATION ${PYLIBELF_BUILD_INSTALL_DIR})
install (FILES pylibelf/__init__.py DESTINATION ${PYLIBELF_BUILD_INSTALL_DIR})

file(COPY "${PYLIBELF_SOURCE_DIR}/.pylintrc" DESTINATION ${CMAKE_CURRENT_BINARY_DIR})

add_test(NAME elf
  COMMAND ${PYLINT} -E "${PYLIBELF_SOURCE_DIR}/src/pylibelf/elf.py"
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})

add_test(NAME libelf
  COMMAND ${PYLINT} -E "${PYLIBELF_SOURCE_DIR}/src/pylibelf/libelf.py"
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})
