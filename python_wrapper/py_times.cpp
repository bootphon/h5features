#include <h5features/times.h>
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>


namespace py = pybind11;
using namespace pybind11::literals;

void init_times(py::module& m)
{
   
   py::class_<h5features::times> times (m, "Times", pybind11::buffer_protocol());
      times.def(pybind11::init([](
            const pybind11::buffer & data ,
            h5features::times::format times_format,
            bool check = true
         ){
         pybind11::buffer_info info = data.request();
         double *p = (double*)info.ptr;
         std::size_t size = data.request().size;
         auto  array = std::vector<double>(p, p+size);
         return h5features::times (array,times_format, check);
      }))
      .def(pybind11::init([](
            const pybind11::buffer & begin_bu ,
            const pybind11::buffer & end_bu ,
            bool check = true
         ){
         pybind11::buffer_info info = begin_bu.request();
         double *p = (double*)info.ptr;
         std::size_t size = begin_bu.request().size;
         auto  begin = std::vector<double>(p, p+size);
         info = end_bu.request();
         p = (double*)info.ptr;
         size = end_bu.request().size;
         auto  end = std::vector<double>(p, p+size);
         return h5features::times (begin,end, check);
      }))
      // .def(py::init(&create_times))
      .def("size", &h5features::times::size)
      .def("get_format", &h5features::times::get_ft)
      .def("dim", &h5features::times::dim)
      .def("start", &h5features::times::start)
      .def("stop", &h5features::times::stop)
      .def("__eq__", &h5features::times::operator==, pybind11::is_operator(), "returns true if the two times instances are equal")
      .def("__ne__", &h5features::times::operator!=, pybind11::is_operator(), "returns true if the two times instances are not equal")      
      .def_buffer( [](h5features::times &times ) -> pybind11::buffer_info {
         double* p=(double*)times.data().data();
         return pybind11::buffer_info(
            p,
            sizeof(double),
            pybind11::format_descriptor<double>::format(),
            1, {times.size()*times.dim()},
            {sizeof(double)});
         
      });
      pybind11::enum_<h5features::times::format>(times, "format")
      .value("simple", h5features::times::format::simple)
      .value("interval", h5features::times::format::interval)
      .export_values();

}
