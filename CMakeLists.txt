cmake_minimum_required(VERSION 3.12 FATAL_ERROR)
message(STATUS "CMake version: ${CMAKE_VERSION}")

#######################################################################
# main project setup
#######################################################################

project(pyh5features
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
option(H5FEATURES_BUILD_TEST "Builds the test suite" OFF)
option(H5FEATURES_BUILD_DOC "Builds the documentation" OFF)


#######################################################################
# find dependencies
#######################################################################


# HighFive (include Boost)
if(NOT DEFINED HIGHFIVE_SOURCE_DIR)
  set(HIGHFIVE_USE_BOOST ON)
  set(HIGHFIVE_EXAMPLES OFF)
  set(HIGHFIVE_UNIT_TESTS OFF)
  set(HIGHFIVE_USE_INSTALL_DEPS YES)
  set(HIGHFIVE_BUILD_DOCS OFF)

  set(HIGHFIVE_SOURCE_DIR ${PROJECT_SOURCE_DIR}/external/HighFive)
  add_subdirectory(${HIGHFIVE_SOURCE_DIR})
endif()


#######################################################################
# h5features library
#######################################################################
if(H5FEATURES_BUILD_PYTHON) # include compilation of Python bindings
  message(STATUS "Compile H5features and wrapper")
  
#  file(GLOB highfive "${PROJECT_SOURCE_DIR}/external/HighFive/include/*h")
#  source_group(TREE ${PROJECT_SOURCE_DIR} FILES ${highfive})
  add_subdirectory(external/pybind11)

  pybind11_add_module(pyh5features
    THIN_LTO
    ${PROJECT_SOURCE_DIR}/python_wrapper/src/item.cpp
    ${PROJECT_SOURCE_DIR}/python_wrapper/src/writer.cpp
    ${PROJECT_SOURCE_DIR}/python_wrapper/src/reader.cpp
    ${PROJECT_SOURCE_DIR}/python_wrapper/py_h5features.cpp
    ${PROJECT_SOURCE_DIR}/python_wrapper/py_item.cpp
    ${PROJECT_SOURCE_DIR}/python_wrapper/py_reader.cpp
    ${PROJECT_SOURCE_DIR}/python_wrapper/py_writer.cpp
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
    ${PROJECT_SOURCE_DIR}/src/v2_writer.cpp
    ${PROJECT_SOURCE_DIR}/src/properties_reader.cpp
    ${PROJECT_SOURCE_DIR}/src/properties_writer.cpp
    ${highfive})

    target_include_directories(pyh5features PUBLIC
    ${PROJECT_SOURCE_DIR}/python_wrapper/include
    ${PROJECT_SOURCE_DIR}/include
    ${HIGHFIVE_SOURCE_DIR}/include)

    target_link_libraries(pyh5features PRIVATE pybind11::module)

else() #compilation without wrapper
message(STATUS "Compile H5features only")
  add_library(pyh5features
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
    ${PROJECT_SOURCE_DIR}/src/v2_writer.cpp
    ${PROJECT_SOURCE_DIR}/src/properties_reader.cpp
    ${PROJECT_SOURCE_DIR}/src/properties_writer.cpp)

    target_include_directories(pyh5features PUBLIC
  ${PROJECT_SOURCE_DIR}/include
  ${HIGHFIVE_SOURCE_DIR}/include)
endif()

target_link_libraries(pyh5features PUBLIC HighFive)


# install the headers and library
install(TARGETS pyh5features
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
  PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})


# execute the tests with "make" and run them with "make test"
if(H5FEATURES_BUILD_TEST)
  enable_testing()
  add_subdirectory(test)

  add_executable(benchmark ${PROJECT_SOURCE_DIR}/test/utils/src/benchmark.cpp)
  target_link_libraries(benchmark pyh5features)
endif()


# build the documentation with "make doc"
if(H5FEATURES_BUILD_DOC)
  add_subdirectory(doc)
endif()
