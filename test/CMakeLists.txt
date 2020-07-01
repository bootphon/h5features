#######################################################################
# build the tests
#######################################################################

find_package(Boost 1.55 COMPONENTS unit_test_framework filesystem)

# compile the test utils library

add_library(h5features-test
  utils/src/test_utils_tmpdir.cpp)
target_include_directories(h5features-test PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/utils/include)
target_link_libraries(h5features-test h5features ${Boost_LIBRARIES})

# compile unit tests

function(add_h5features_test name)
  add_executable(${name} src/${name}.cpp)
  target_link_libraries(${name} h5features-test)
  add_test(${name} ${name})
endfunction()

add_h5features_test(test_features)
add_h5features_test(test_item)
add_h5features_test(test_properties)
add_h5features_test(test_reader)
add_h5features_test(test_times)
add_h5features_test(test_writer)
