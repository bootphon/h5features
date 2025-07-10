find_package(Python 3.12
  REQUIRED COMPONENTS Interpreter Development.Module
  OPTIONAL_COMPONENTS Development.SABIModule)

find_package(nanobind CONFIG REQUIRED)

nanobind_add_module(
  _core
  STABLE_ABI
  LTO
  NB_STATIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src/py_h5features.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/src/py_item.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/src/py_reader.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/src/py_version.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/src/py_writer.cpp
)

target_include_directories(_core PUBLIC
  ${PROJECT_SOURCE_DIR}/include
  ${HIGHFIVE_SOURCE_DIR}/include
)

target_link_libraries(_core PRIVATE h5features)

nanobind_add_stub(
  _core_stub
  MODULE _core
  OUTPUT _core.pyi
  MARKER_FILE py.typed
  DEPENDS _core
)

install(TARGETS _core LIBRARY DESTINATION h5features)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/py.typed" DESTINATION h5features)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/_core.pyi" DESTINATION h5features)

if(APPLE)
  set_target_properties(_core PROPERTIES INSTALL_RPATH "@loader_path/../${CMAKE_INSTALL_LIBDIR}")
else()
  set_target_properties(_core PROPERTIES INSTALL_RPATH "$ORIGIN/../${CMAKE_INSTALL_LIBDIR}")
endif()

# include the Python tests with "make test"
if(H5FEATURES_BUILD_TEST)
  find_package(Python3 REQUIRED COMPONENTS Interpreter)

  add_test(
    NAME test_python
    COMMAND ${Python3_EXECUTABLE} -m pytest ${CMAKE_CURRENT_SOURCE_DIR}/test)

  # need to tweak PYTHONPATH so as to find the _core library (either in
  # BINARY_DIR if using "python setup.py install" / cmake, or in SOURCE_DIR if
  # using "python setup.py develop")
  set_tests_properties(test_python
    PROPERTIES ENVIRONMENT "PYTHONPATH=${CMAKE_CURRENT_SOURCE_DIR}:${CMAKE_CURRENT_BINARY_DIR}:$PYTHONPATH")
endif()
