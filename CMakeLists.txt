cmake_minimum_required(VERSION 3.5)
project(cmake_wrapper)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

# make compile as submodule
include_directories("source_subfolder/src")
add_subdirectory("source_subfolder")
