#######################################################################
# build the tests
#######################################################################

find_package(Boost 1.55 REQUIRED COMPONENTS unit_test_framework filesystem)

# compile the test utils library

add_library(h5features-test
  utils/src/test_utils_capture.cpp
  utils/src/test_utils_data.cpp
  utils/src/test_utils_tmpdir.cpp)
target_include_directories(
  h5features-test PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/utils/include)
target_link_libraries(
  h5features-test h5features ${Boost_LIBRARIES})

# compile unit tests

function(add_h5features_test name)
  set(src_file ${CMAKE_CURRENT_SOURCE_DIR}/src/${name}.cpp)

  # inhibate an error in boost-1.71: -Werror=sign-compare
  if(${Boost_VERSION_MINOR} GREATER_EQUAL 71)
    set_source_files_properties(
      ${src_file} PROPERTIES COMPILE_OPTIONS "-Wno-sign-compare")
  endif()

  add_executable(${name} ${src_file})
  target_link_libraries(${name} h5features-test)
  add_test(${name} ${name})
endfunction()

add_h5features_test(test_features)
add_h5features_test(test_item)
add_h5features_test(test_properties)
add_h5features_test(test_reader)
add_h5features_test(test_times)
add_h5features_test(test_writer)
