# build the documentation with "make doc", this requires python3 and doxygen

find_package(Python3 REQUIRED COMPONENTS Interpreter)
find_program(DOXYGEN doxygen REQUIRED)


# configure Doxyfile.in and conf.py.in
configure_file(
  ${CMAKE_CURRENT_SOURCE_DIR}/Doxyfile.in
  ${CMAKE_CURRENT_BINARY_DIR}/Doxyfile
  @ONLY)

configure_file(
  ${CMAKE_CURRENT_SOURCE_DIR}/conf.py.in
  ${CMAKE_CURRENT_BINARY_DIR}/conf.py
  @ONLY)


# install dependencies for documentation building
set(PIP_DEPENDENCIES breathe Sphinx sphinx_rtd_theme sphinxcontrib-napoleon)
execute_process(
  COMMAND mkdir -p ${PROJECT_BINARY_DIR}/pip
  COMMAND ${Python3_EXECUTABLE} -m pip install --upgrade --target ${PROJECT_BINARY_DIR}/pip ${PIP_DEPENDENCIES})

add_custom_target(doc
  COMMAND ${DOXYGEN}
  COMMAND ${Python3_EXECUTABLE} ${PROJECT_BINARY_DIR}/pip/bin/sphinx-build -c. ${CMAKE_CURRENT_SOURCE_DIR} ./html
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
  COMMENT "Generating API documentation"
  VERBATIM)

# install documentation
install(
  DIRECTORY    ${CMAKE_CURRENT_BINARY_DIR}/html/
  DESTINATION  share/doc/${PROJECT_NAME})
