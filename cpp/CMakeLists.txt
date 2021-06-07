#######################################################################
# h5features library
#######################################################################


# HighFive (include Boost)
if(NOT DEFINED HIGHFIVE_SOURCE_DIR)
  set(HIGHFIVE_USE_BOOST ON)
  set(HIGHFIVE_EXAMPLES OFF)
  set(HIGHFIVE_UNIT_TESTS OFF)
  set(HIGHFIVE_USE_INSTALL_DEPS YES)
  set(HIGHFIVE_BUILD_DOCS OFF)

  set(HIGHFIVE_SOURCE_DIR ${PROJECT_SOURCE_DIR}/external/HighFive)
  add_subdirectory(
    ${HIGHFIVE_SOURCE_DIR}
    ${PROJECT_BINARY_DIR}/external/HighFive)
endif()


configure_file(
  include/h5features.h.in
  generated/h5features.h
  @ONLY)

add_library(h5features
  ${CMAKE_CURRENT_SOURCE_DIR}/src/item.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/src/features.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/src/times.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/src/properties.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/src/version.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/src/exception.cpp
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
  ${CMAKE_CURRENT_BINARY_DIR}/generated
  ${HIGHFIVE_SOURCE_DIR}/include)

target_link_libraries(h5features PUBLIC HighFive)


# install the headers and library
install(TARGETS h5features
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
  PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})


# execute the tests with "make" and run them with "make test"
if(H5FEATURES_BUILD_TEST)
  enable_testing()
  add_subdirectory(test)

  add_executable(benchmark ${PROJECT_SOURCE_DIR}/test/utils/src/benchmark.cpp)
  target_link_libraries(benchmark h5features)
endif()
