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
  PYTHON_PATH $<TARGET_FILE_DIR:_core>
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
