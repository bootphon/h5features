cmake_minimum_required(VERSION 3.15 FATAL_ERROR)
message(STATUS "CMake version: ${CMAKE_VERSION}")

#######################################################################
# main project setup
#######################################################################


# read H5FEATURES_VERSION from file
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/VERSION")
  file(READ "${CMAKE_CURRENT_SOURCE_DIR}/VERSION" H5FEATURES_VERSION)
  string(STRIP "${H5FEATURES_VERSION}" H5FEATURES_VERSION)
else()
  message(FATAL_ERROR "File ${CMAKE_CURRENT_SOURCE_DIR}/VERSION not found")
endif()


project(h5features
  VERSION ${H5FEATURES_VERSION}
  DESCRIPTION "easy and efficient storage of large features data on HDF5 file format"
  LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)


if (MSVC)
  # warning level 3 and all warnings as errors. Disable C4244.
  add_compile_options(/W3 /WX /permissive- /wd4244)
else()
  # lots of warnings and all warnings as errors
  add_compile_options(-Wall -Wextra -Werror)
endif()

include(GNUInstallDirs)

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

if(SKBUILD STREQUAL "2" AND MSVC) # On Windows with the python extension: static libraries
  option(BUILD_SHARED_LIBS "Builds shared libraries" OFF)
else()
  option(BUILD_SHARED_LIBS "Builds shared libraries" ON)
endif()

option(H5FEATURES_BUILD_TEST "Builds the test suite" OFF)


#######################################################################
# h5features C++ library
#######################################################################


# HDF5, request 1.10 minimum
if(NOT DEFINED HDF5_C_LIBRARIES)
  set(HDF5_NO_FIND_PACKAGE_CONFIG_FILE TRUE)
  set(HDF5_PREFER_PARALLEL TRUE)
  find_package(HDF5 1.10 REQUIRED)
endif()


# HighFive
if(NOT DEFINED HIGHFIVE_SOURCE_DIR)
  set(HIGHFIVE_SOURCE_DIR ${PROJECT_SOURCE_DIR}/external/HighFive)
  add_subdirectory(
    ${HIGHFIVE_SOURCE_DIR}
    ${PROJECT_BINARY_DIR}/external/HighFive)
endif()


configure_file(
  include/h5features.h.in
  include/h5features.h
  @ONLY)

add_library(h5features
  ${CMAKE_CURRENT_SOURCE_DIR}/src/item.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/src/features.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/src/times.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/src/properties.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/src/version.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/src/reader.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/src/reader_interface.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/src/v1_reader.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/src/v2_reader.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/src/writer.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/src/writer_interface.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/src/v1_writer.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/src/v2_writer.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/src/properties_reader.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/src/properties_writer.cpp)

target_include_directories(h5features PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/include
  ${CMAKE_CURRENT_BINARY_DIR}/include
  ${HIGHFIVE_SOURCE_DIR}/include)

target_link_libraries(h5features PUBLIC HighFive)


# install the headers and library
install(TARGETS h5features
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR})

install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/include/
  DESTINATION "include"
  PATTERN "*.in" EXCLUDE)

install(DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/include/
  DESTINATION "include")

# execute the tests with "make" and run them with "make test"
if(H5FEATURES_BUILD_TEST)
  enable_testing()
  add_subdirectory(test)

  add_executable(benchmark ${CMAKE_CURRENT_SOURCE_DIR}/test/utils/src/benchmark.cpp)
  target_link_libraries(benchmark h5features)
endif()

# h5features Python library
if(SKBUILD STREQUAL "2")
  add_subdirectory(python)
endif()
