# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2022-2023 Advanced Micro Devices, Inc.

cmake_minimum_required(VERSION 3.18.0)

project(py-elflib)

if (${CMAKE_SYSTEM_NAME} STREQUAL "Linux")
  set(CMAKE_INSTALL_PREFIX "/opt/xilinx/py-libelf")
else()
  message(FATAL_ERROR "Unsupported platform")
endif()

find_package(PkgConfig REQUIRED)
pkg_check_modules(LIBELF REQUIRED libelf)
find_package(Python3 COMPONENTS Interpreter REQUIRED)

if (Python3_FOUND)
  message("-- Python version: ${Python3_VERSION}")
  set(PYTHONLIBS_VERSION_MAJOR ${Python3_VERSION_MAJOR})
  set(PYTHONLIBS_VERSION_MINOR ${Python3_VERSION_MINOR})
endif(Python3_FOUND)
message("-- CMAKE_INSTALL_PREFIX=${CMAKE_INSTALL_PREFIX}")

find_program (PYLINT pylint REQUIRED)

set (PY_ELFLIB_INSTALL_DIR "pyelflib")
set (PY_ELFLIB_BUILD_INSTALL_DIR "${CMAKE_BINARY_DIR}${CMAKE_INSTALL_PREFIX}/${PY_ELFLIB_INSTALL_DIR}")

enable_testing()

add_subdirectory(src)
add_subdirectory(test)
