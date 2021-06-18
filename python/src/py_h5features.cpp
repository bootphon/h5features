#include <pybind11/pybind11.h>
#include <pybind11/iostream.h>
// use of several .cpp files to reduce the compilation time

void init_item(pybind11::module& m);
void init_reader(pybind11::module& m);
void init_writer(pybind11::module& m);
void init_read_group(pybind11::module& m);
void init_version(pybind11::module& m);


PYBIND11_MODULE(_h5features, m)
{
   // redirection of std::{cout,cerr} to sys.std{out,err}
   pybind11::add_ostream_redirect(m, "ostream_redirect");

   init_item(m);
   init_reader(m);
   init_writer(m);
   init_read_group(m);
   init_version(m);
}
