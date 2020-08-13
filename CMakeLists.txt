cmake_minimum_required(VERSION 3.10 FATAL_ERROR)
message(STATUS "CMake version: ${CMAKE_VERSION}")

#######################################################################
# main project setup
#######################################################################

project(h5features
  VERSION 2.0.0
  DESCRIPTION "easy and efficient storage of large features data on HDF5 file format"
  LANGUAGES C CXX)
set(PROJECT_AUTHOR "Mathieu Bernard <mathieu.a.bernard@inria.fr>")
set(PROJECT_COPYRIGHT "2020 Inria")

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)


if (MSVC)
  # warning level 4 and all warnings as errors
  add_compile_options(/W4 /WX)
else()
  # lots of warnings and all warnings as errors
  add_compile_options(-Wall -Wextra -pedantic -Werror)
endif()


#######################################################################
# cmake build configuration
#######################################################################

# Set a default build type if none was specified
set(default_build_type "Release")
if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  message(STATUS "Setting build type to '${default_build_type}' as none was specified.")
  set(CMAKE_BUILD_TYPE "${default_build_type}" CACHE
    STRING "Choose the type of build." FORCE)
  # Set the possible values of build type for cmake-gui
  set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS
    "Debug" "Release" "MinSizeRel" "RelWithDebInfo")
endif()

option(BUILD_SHARED_LIBS "Builds shared libraries" ON)
option(H5FEATURES_BUILD_PYTHON "Builds the Python wrapper" ON)
option(H5FEATURES_BUILD_BENCHMARK "Builds the benchmark" OFF)
option(H5FEATURES_BUILD_TEST "Builds the test suite" ON)
option(H5FEATURES_BUILD_DOC "Builds the documentation" ON)


#######################################################################
# find dependencies
#######################################################################

# HDF5 (require 1.10 minimum, after
# ${HIGHFIVE_SOURCE_DIR}/CMake/HighFiveTargetDeps.cmake)
set(HDF5_NO_FIND_PACKAGE_CONFIG_FILE TRUE)  # Consistency
set(HDF5_PREFER_PARALLEL ${HIGHFIVE_PARALLEL_HDF5})
find_package(HDF5 1.10 REQUIRED)

# HighFive (include Boost)
set(HIGHFIVE_SOURCE_DIR ${PROJECT_SOURCE_DIR}/external/HighFive)
list(APPEND CMAKE_MODULE_PATH
  ${HIGHFIVE_SOURCE_DIR}/CMake
  ${HIGHFIVE_SOURCE_DIR}/CMake/portability
  ${HIGHFIVE_SOURCE_DIR}/CMake/config)
set(HIGHFIVE_USE_BOOST ON)
include(${HIGHFIVE_SOURCE_DIR}/CMake/HighFiveTargetDeps.cmake)
include(${HIGHFIVE_SOURCE_DIR}/CMake/HighFiveTargetExport.cmake)


#######################################################################
# h5features library
#######################################################################

add_library(h5features
  ${PROJECT_SOURCE_DIR}/src/item.cpp
  ${PROJECT_SOURCE_DIR}/src/features.cpp
  ${PROJECT_SOURCE_DIR}/src/times.cpp
  ${PROJECT_SOURCE_DIR}/src/properties.cpp
  ${PROJECT_SOURCE_DIR}/src/version.cpp
  ${PROJECT_SOURCE_DIR}/src/exception.cpp
  ${PROJECT_SOURCE_DIR}/src/reader.cpp
  ${PROJECT_SOURCE_DIR}/src/reader_interface.cpp
  ${PROJECT_SOURCE_DIR}/src/v1_reader.cpp
  ${PROJECT_SOURCE_DIR}/src/v2_reader.cpp
  ${PROJECT_SOURCE_DIR}/src/writer.cpp
  ${PROJECT_SOURCE_DIR}/src/writer_interface.cpp
  ${PROJECT_SOURCE_DIR}/src/v1_writer.cpp
  ${PROJECT_SOURCE_DIR}/src/v2_writer.cpp)
target_include_directories(h5features PUBLIC
  ${PROJECT_SOURCE_DIR}/include
  ${HIGHFIVE_SOURCE_DIR}/include)
target_link_libraries(h5features HighFive)


add_executable(basic ${PROJECT_SOURCE_DIR}/src/basic.cpp)
target_link_libraries(basic h5features)


if(H5FEATURES_BUILD_PYTHON)
  add_subdirectory(external/pybind11)
  add_subdirectory(python)
endif()

# execute the tests with "make test"
if(H5FEATURES_BUILD_TEST)
  enable_testing()
  add_subdirectory(test)
endif()


# build the documentation with "make doc"
if(H5FEATURES_BUILD_DOC)
  add_subdirectory(doc)
endif()


# build the benchmark with "make benchmark"
if(H5FEATURES_BUILD_BENCHMARK)
  add_executable(benchmark ${PROJECT_SOURCE_DIR}/test/utils/src/benchmark.cpp)
  target_link_libraries(benchmark h5features)
endif()
