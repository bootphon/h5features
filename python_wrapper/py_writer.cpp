#include <h5features/writer.h>
#include <pybind11/pybind11.h>


void init_writer(pybind11::module& m)
{
   pybind11::class_<h5features::writer>(m, "Writer");
}
