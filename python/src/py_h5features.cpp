#include <pybind11/pybind11.h>
#include <pybind11/iostream.h>


// use of several .cpp files to reduce the compilation time
void init_item(pybind11::module& m);
void init_reader(pybind11::module& m);
void init_writer(pybind11::module& m);
void init_properties(pybind11::module& m);
void init_version(pybind11::module& m);


PYBIND11_MODULE(_h5features, m)
{
   // redirection from C++ std::{cout,cerr} to Python sys.std{out,err}
   pybind11::add_ostream_redirect(m, "OstreamRedirect");

   init_item(m);
   init_reader(m);
   init_writer(m);
   init_properties(m);
   init_version(m);
}
