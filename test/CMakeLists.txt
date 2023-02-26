# SPDX-License-Identifier: MIT
# Copyright (C) 2023 Advanced Micro Devices, Inc.

message("-- CMAKE_CURRENT_BINARY_DIR=${CMAKE_CURRENT_BINARY_DIR}")

file(COPY "${PYLIBELF_SOURCE_DIR}/.pylintrc" DESTINATION ${CMAKE_CURRENT_BINARY_DIR})

foreach(sample libelf-classic multiple-sections strtab)

  add_test(NAME ${sample}
    COMMAND "${PYLIBELF_SOURCE_DIR}/test/${sample}.py" "-o" "${sample}.elf" "-r"
    "${PYLIBELF_SOURCE_DIR}/test/${sample}.gold" WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})

  add_test(NAME "${sample}_read"
    COMMAND "${PYLIBELF_SOURCE_DIR}/test/${sample}.py" "-d" "${sample}.elf"
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})

  set_tests_properties(${sample} "${sample}_read" PROPERTIES ENVIRONMENT
    "PYTHONPATH=${PYLIBELF_SOURCE_DIR}/src")

endforeach()

#add_test(NAME libelf-classic
#  COMMAND "${PYLIBELF_SOURCE_DIR}/test/libelf-classic.py" "-o" "libelf-classic.elf" "-r"
#  "${PYLIBELF_SOURCE_DIR}/test/libelf-classic.gold" WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})

#add_test(NAME multiple-sections
#  COMMAND "${PYLIBELF_SOURCE_DIR}/test/multiple-sections.py" "-o" "multiple-sections.elf" "-r"
#  "${PYLIBELF_SOURCE_DIR}/test/multiple-sections.gold" WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})

#add_test(NAME strtab
#  COMMAND "${PYLIBELF_SOURCE_DIR}/test/strtab.py" "-o" "strtab.elf" "-r"
#  "${PYLIBELF_SOURCE_DIR}/test/strtab.gold" WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})

#set_tests_properties(libelf-classic multiple-sections strtab PROPERTIES ENVIRONMENT
#  "PYTHONPATH=${PYLIBELF_SOURCE_DIR}/src")
