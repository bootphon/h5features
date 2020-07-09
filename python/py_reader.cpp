#include <h5features/reader.h>
#include <pybind11/pybind11.h>


void init_reader(pybind11::module& m)
{
   pybind11::class_<h5features::reader>(m, "Reader");
}
