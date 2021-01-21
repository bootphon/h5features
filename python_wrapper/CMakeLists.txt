
pybind11_add_module(pyh5features THIN_LTO
  ${CMAKE_CURRENT_SOURCE_DIR}/py_h5features.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/py_features.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/py_times.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/py_properties.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/py_item.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/py_reader.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/py_writer.cpp)
target_link_libraries(pyh5features PRIVATE pybind11::module h5features)
target_include_directories(pyh5features PUBLIC
  ${PROJECT_SOURCE_DIR}/include
  ${HIGHFIVE_SOURCE_DIR}/include)
