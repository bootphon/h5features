# build the documentation with "make doc", this requires python3 and doxygen

find_program(DOXYGEN doxygen)
if(NOT DOXYGEN)
  message(FATAL_ERROR "Doxygen is needed to build the documentation.")
endif()

find_program(PYTHON3 python3)
if(NOT PYTHON3)
  message(FATAL_ERROR "Python3 is needed to build the documentation.")
endif()


# configure Doxyfile.in
set(doxyfile_in ${CMAKE_CURRENT_SOURCE_DIR}/Doxyfile.in)
set(doxyfile ${CMAKE_CURRENT_BINARY_DIR}/Doxyfile)
configure_file(${doxyfile_in} ${doxyfile} @ONLY)

# configure conf.py.in
set(conf_py_in ${CMAKE_CURRENT_SOURCE_DIR}/conf.py.in)
set(conf_py ${CMAKE_CURRENT_BINARY_DIR}/conf.py)
configure_file(${conf_py_in} ${conf_py} @ONLY)


# install dependencies for documentation building
execute_process(
  COMMAND ${PYTHON3} -m pip install --upgrade --user breathe sphinx sphinx_rtd_theme)

# build the documentation
add_custom_target(doc
  COMMAND ${DOXYGEN}
  COMMAND sphinx-build -c. ${CMAKE_CURRENT_SOURCE_DIR} ./html
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
  COMMENT "Generating API documentation with Doxygen and Sphinx"
  VERBATIM)

# install documentation
install(
  DIRECTORY    ${CMAKE_CURRENT_BINARY_DIR}/html/
  DESTINATION  share/doc/libdistance)
