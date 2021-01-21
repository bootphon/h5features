#include <h5features/times.h>
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>


namespace py = pybind11;
using namespace pybind11::literals;

h5features::times create_times(
   const py::array_t<double, py::array::c_style | py::array::forcecast>& array,
   const std::string& format,
   bool validate=true)
{
   std::vector<double> array_vec(array.size());
   std::memcpy(array_vec.data(),array.data(),array.size()*sizeof(double));

   auto s = format;
   return h5features::times(array_vec, h5features::times::format::simple, validate);
}

void init_times(py::module& m)
{
   // py::class_<h5features::times>(m, "Times", py::buffer_protocol())
   //    .def_buffer([](h5features::times &times) -> py::buffer_info {
   //                   return py::buffer_info(
   //                      times.data().data(),
   //                      sizeof(double),
   //                      py::format_descriptor<double>::format(),
   //                      times.dim(),
   //                      {times.dim(), times.size()},
   //                      {sizeof(double) * times.size(), sizeof(double)}
   //                      );
   //                });
   py::class_<h5features::times>(m, "Times")
      .def(py::init(&create_times))
      .def("size", &h5features::times::size)
      .def("dim", &h5features::times::dim)
      .def("data", &h5features::times::data)
      .def("start", &h5features::times::start)
      .def("stop", &h5features::times::stop)
      .def("validate", &h5features::times::validate);
}
