#include <h5features/times.h>
#include <pybind11/pybind11.h>


void init_times(pybind11::module& m)
{
   pybind11::class_<h5features::times>(m, "Times");
}
