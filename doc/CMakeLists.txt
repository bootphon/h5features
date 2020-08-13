# build the documentation with "make doc", this requires python3 and doxygen

find_package(Python3 REQUIRED COMPONENTS Interpreter)
find_program(DOXYGEN doxygen REQUIRED)

message(STATUS "Creating Python virtual environment in ${PROJECT_BINARY_DIR}/venv")
execute_process(COMMAND "${Python3_EXECUTABLE}" -m venv "${PROJECT_BINARY_DIR}/venv")

# use the Python3 executable from the virtual environment
set(ENV{VIRTUAL_ENV} "${PROJECT_BINARY_DIR}/venv")
set(Python3_FIND_VIRTUALENV FIRST)
unset (Python3_EXECUTABLE)
find_package(Python3 COMPONENTS Interpreter)

message(STATUS "Installing dependencies for documentation build: breathe sphinx_rtd_theme")
execute_process(COMMAND "${Python3_EXECUTABLE}" -m pip install --upgrade pip setuptools OUTPUT_QUIET)
execute_process(COMMAND "${Python3_EXECUTABLE}" -m pip install breathe sphinx_rtd_theme OUTPUT_QUIET)
find_program(SPHINX_BUILD sphinx-build PATHS ${PROJECT_BINARY_DIR}/venv/bin REQUIRED)


# configure Doxyfile.in
set(doxyfile_in ${CMAKE_CURRENT_SOURCE_DIR}/Doxyfile.in)
set(doxyfile ${CMAKE_CURRENT_BINARY_DIR}/Doxyfile)
configure_file(${doxyfile_in} ${doxyfile} @ONLY)

# configure conf.py.in
set(conf_py_in ${CMAKE_CURRENT_SOURCE_DIR}/conf.py.in)
set(conf_py ${CMAKE_CURRENT_BINARY_DIR}/conf.py)
configure_file(${conf_py_in} ${conf_py} @ONLY)


# build the documentation
add_custom_target(doc
  COMMAND ${DOXYGEN}
  COMMAND ${SPHINX_BUILD} -c. ${CMAKE_CURRENT_SOURCE_DIR} ./html
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
  COMMENT "Generating API documentation"
  VERBATIM)

# install documentation
install(
  DIRECTORY    ${CMAKE_CURRENT_BINARY_DIR}/html/
  DESTINATION  share/doc/${PROJECT_NAME})
