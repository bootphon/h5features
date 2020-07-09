#include <h5features/properties.h>
#include <pybind11/pybind11.h>


void init_properties(pybind11::module& m)
{
   pybind11::class_<h5features::properties>(m, "Properties");
}
