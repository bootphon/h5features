add_subdirectory(
  ${PROJECT_SOURCE_DIR}/external/pybind11
  ${PROJECT_BINARY_DIR}/external/pybind11)

pybind11_add_module(_h5features
  THIN_LTO
  ${CMAKE_CURRENT_SOURCE_DIR}/src/item.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/src/writer.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/src/reader.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/src/py_h5features.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/src/py_item.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/src/py_reader.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/src/py_writer.cpp)

target_include_directories(_h5features PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/include
  ${PROJECT_SOURCE_DIR}/include
  ${HIGHFIVE_SOURCE_DIR}/include)

target_link_libraries(_h5features PRIVATE pybind11::module h5features)


# include the Python tests with "make test"
if(H5FEATURES_BUILD_TEST)
  find_package(Python3 REQUIRED COMPONENTS Interpreter)

  add_test(
    NAME test_python
    COMMAND ${Python3_EXECUTABLE} -m pytest ${CMAKE_CURRENT_SOURCE_DIR}/test)

  # need to tweak PYTHONPATH so as to find the _h5features library (either in
  # BINARY_DIR if using "python setup.py install" / cmake, or in SOURCE_DIR if
  # using "python setup.py develop")
  set_tests_properties(test_python
    PROPERTIES ENVIRONMENT "PYTHONPATH=${CMAKE_CURRENT_SOURCE_DIR}:${CMAKE_CURRENT_BINARY_DIR}:$PYTHONPATH")
endif()
