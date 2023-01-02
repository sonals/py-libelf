# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2022 Advanced Micro Devices, Inc.

cmake_minimum_required(VERSION 3.18.0)

project(py-elflib)

if (${CMAKE_SYSTEM_NAME} STREQUAL "Linux")
  if(CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)
    set(CMAKE_INSTALL_PREFIX "/opt/xilinx/py-libelf")
    message("-- Install prefix is default initialized to ${CMAKE_INSTALL_PREFIX}")
  endif()
else()
  message(FATAL_ERROR "Unsupported platform")
endif()

find_package(Python3 COMPONENTS Interpreter REQUIRED)
if (Python3_FOUND)
  message("-- Python libs version: ${Python3_VERSION}")
  set(PYTHONLIBS_VERSION_MAJOR ${Python3_VERSION_MAJOR})
  set(PYTHONLIBS_VERSION_MINOR ${Python3_VERSION_MINOR})
endif(Python3_FOUND)
message("-- CMAKE_INSTALL_PREFIX=${CMAKE_INSTALL_PREFIX}")

find_program (PYLINT pylint REQUIRED)

set (PY_ELFLIB_INSTALL_DIR "pyelflib")
set (PY_ELFLIB_BUILD_INSTALL_DIR "${CMAKE_BINARY_DIR}${CMAKE_INSTALL_PREFIX}/${PY_ELFLIB_INSTALL_DIR}")

# Enable testing for this directory and below.  This command should be
# in the source directory root because ctest expects to find a test
# file in the build directory root.
enable_testing()

add_subdirectory(src)
add_subdirectory(test)
