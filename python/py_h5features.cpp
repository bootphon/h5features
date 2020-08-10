#include <pybind11/pybind11.h>

// use of several .cpp files to reduce the compilation time

void init_features(pybind11::module& m);
void init_times(pybind11::module& m);
void init_properties(pybind11::module& m);
void init_item(pybind11::module& m);
void init_reader(pybind11::module& m);
void init_writer(pybind11::module& m);


PYBIND11_MODULE(py_h5features, m)
{
   init_features(m);
   init_times(m);
   init_properties(m);
   init_item(m);
   init_reader(m);
   init_writer(m);
}
