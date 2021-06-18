#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include "item_wrapper.h"


void init_item(pybind11::module& m)
{
   pybind11::class_<item_wrapper>(m, "ItemWrapper", pybind11::buffer_protocol())
      .def(pybind11::init([](
         const std::string& name,
         const pybind11::buffer& features,
         const pybind11::array_t<double, pybind11::array::c_style>& times,
         const pybind11::dict& properties,
         bool check = true)
         {
            // create features object
            pybind11::buffer_info info = features.request();
            double *ptr = static_cast<double*>(info.ptr);
            h5features::features cfeatures{
               std::vector<double>{ptr, ptr + info.size},
               static_cast<std::size_t>(info.shape[1]),
               check};

            // create times object
            info = times.request();
            ptr = static_cast<double*>(info.ptr);
            h5features::times ctimes{
               std::vector<double>{ptr, ptr + info.size},
               h5features::times::get_format(info.shape[1]),
               check};

            // create properties object
            auto props = pybind11::handle(properties).cast<h5features::properties>();

            // instanciate item object
            return item_wrapper(name, cfeatures, ctimes, props, check);
         }))
      .def("__eq__", &item_wrapper::operator==, pybind11::is_operator())
      .def("__ne__", &item_wrapper::operator!=, pybind11::is_operator())
      .def("name", &item_wrapper::name)
      .def("has_properties", &item_wrapper::has_properties)
      .def("dim", &item_wrapper::dim)
      .def("size",&item_wrapper::size)
      .def("features", &item_wrapper::features)
      .def("times", &item_wrapper::times)
      .def("properties", &item_wrapper::properties);
}
