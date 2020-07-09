#include <h5features/features.h>
#include <pybind11/pybind11.h>


void init_features(pybind11::module& m)
{
   pybind11::class_<h5features::features>(m, "Features");
}
