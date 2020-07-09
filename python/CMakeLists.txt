find_package(pybind11 REQUIRED)

pybind11_add_module(_h5features THIN_LTO
  ${CMAKE_CURRENT_SOURCE_DIR}/py_h5features.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/py_features.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/py_times.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/py_properties.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/py_item.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/py_reader.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/py_writer.cpp)
target_link_libraries(_h5features PRIVATE pybind11::module h5features)
target_include_directories(_h5features PUBLIC
  ${PROJECT_SOURCE_DIR}/include
  ${HIGHFIVE_SOURCE_DIR}/include)
