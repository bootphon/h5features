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
