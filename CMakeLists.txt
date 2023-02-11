# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2022-2023 Advanced Micro Devices, Inc.

cmake_minimum_required(VERSION 3.18.0)

project(PYLIBELF HOMEPAGE_URL https://github.com/sonals/py-libelf)

if (${CMAKE_SYSTEM_NAME} STREQUAL "Linux")
  set(CMAKE_INSTALL_PREFIX "/opt/xilinx")
else()
  message(FATAL_ERROR "Unsupported platform")
endif()

message("-- CMAKE_SYSTEM=${CMAKE_SYSTEM}")
message("-- CMAKE_INSTALL_PREFIX=${CMAKE_INSTALL_PREFIX}")

find_package(PkgConfig REQUIRED)

pkg_check_modules(LIBELF REQUIRED libelf)
message("-- Libelf version: ${LIBELF_VERSION}")

find_package(Python3 COMPONENTS Interpreter REQUIRED)
message("-- Python version: ${Python3_VERSION}")

find_program (PYLINT pylint REQUIRED)

set (PYLIBELF_INSTALL_DIR "pylibelf")
set (PYLIBELF_BUILD_INSTALL_DIR "${CMAKE_BINARY_DIR}${CMAKE_INSTALL_PREFIX}/${PYLIBELF_INSTALL_DIR}")

enable_testing()

add_subdirectory(src)
add_subdirectory(test)
