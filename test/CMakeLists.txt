#######################################################################
# build the tests
#######################################################################

find_package(Boost 1.55 REQUIRED COMPONENTS unit_test_framework filesystem)

# configure test data directory as test/data

set(H5FEATURES_TEST_DATA_DIR ${CMAKE_CURRENT_BINARY_DIR}/data)

file(
  COPY "${CMAKE_CURRENT_SOURCE_DIR}/data/data.1.0.h5f"
  DESTINATION ${H5FEATURES_TEST_DATA_DIR})
file(
  COPY "${CMAKE_CURRENT_SOURCE_DIR}/data/data.1.1.h5f"
  DESTINATION ${H5FEATURES_TEST_DATA_DIR})
file(
  COPY "${CMAKE_CURRENT_SOURCE_DIR}/data/data.2.0.h5f"
  DESTINATION ${H5FEATURES_TEST_DATA_DIR})

configure_file(
  ${CMAKE_CURRENT_SOURCE_DIR}/utils/src/test_utils_datadir.cpp.in
  ${CMAKE_CURRENT_BINARY_DIR}/utils/src/test_utils_datadir.cpp)

# compile the test utils library

add_library(h5features-test
  ${CMAKE_CURRENT_SOURCE_DIR}/utils/src/test_utils_capture.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/utils/src/test_utils_data.cpp
  ${CMAKE_CURRENT_BINARY_DIR}/utils/src/test_utils_datadir.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/utils/src/test_utils_tmpdir.cpp)
target_include_directories(
  h5features-test PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/utils/include
  ${PROJECT_SOURCE_DIR}/include)
target_link_libraries(
  h5features-test ${Boost_LIBRARIES} HighFive)

# compile unit tests

function(add_h5features_test name)
  set(src_file ${CMAKE_CURRENT_SOURCE_DIR}/src/${name}.cpp)

  # inhibate an error in boost-1.71: -Werror=sign-compare
  if(${Boost_VERSION_MINOR} GREATER_EQUAL 71)
    set_source_files_properties(
      ${src_file} PROPERTIES COMPILE_OPTIONS "-Wno-sign-compare")
  endif()

  add_executable(${name} ${src_file})
  target_include_directories(${name} PUBLIC ${HIGHFIVE_SOURCE_DIR}/include)
  target_link_libraries(${name} h5features-test h5features)
  add_test(${name} ${name})
endfunction()

add_h5features_test(test_features)
add_h5features_test(test_item)
add_h5features_test(test_properties)
add_h5features_test(test_reader)
add_h5features_test(test_reader_files)
add_h5features_test(test_times)
add_h5features_test(test_writer)
