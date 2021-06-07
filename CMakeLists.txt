cmake_minimum_required(VERSION 3.12 FATAL_ERROR)
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
set(PROJECT_AUTHOR "CoML <https://cognitive-ml.fr>")
set(PROJECT_COPYRIGHT "2020-2021 Inria")

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
option(H5FEATURES_BUILD_TEST "Builds the test suite" OFF)
option(H5FEATURES_BUILD_DOC "Builds the documentation" OFF)


# h5features C++ library
add_subdirectory(cpp)


# h5features Python library
if(H5FEATURES_BUILD_PYTHON)
  add_subdirectory(python)
endif()


# build the documentation with "make doc"
if(H5FEATURES_BUILD_DOC)
  target_include_directories(h5features PUBLIC h5features)
  add_subdirectory(doc)
endif()
