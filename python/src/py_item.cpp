#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include "item_wrapper.h"


void init_item(pybind11::module& m)
{
   pybind11::class_<item_wrapper>(m, "ItemWrapper", pybind11::buffer_protocol())
      .def(pybind11::init([](
         const std::string& name,
         const pybind11::buffer & features,
         const pybind11::buffer & begin,
         const pybind11::buffer & end,
         const pybind11::dict & properties,
         bool check = true){
            // create features object
            pybind11::buffer_info info = features.request();
            double *p = (double*)info.ptr;
            std::size_t size = info.size;
            std::size_t shape= info.shape[1];
            auto array = std::vector<double>(p, p+size);
            auto feats = h5features::features(array, shape, check);

            // create times object
            info = begin.request();
            p = (double*)info.ptr;
            size = info.size;
            auto begs = std::vector<double>(p, p+size);
            info = end.request();
            p = (double*)info.ptr;
            auto ens = std::vector<double>(p, p+size);
            auto tims = h5features::times(begs, ens, check);

            // create properties object
            auto props = pybind11::handle(properties).cast<h5features::properties>();
            return item_wrapper(name, feats, tims, props, check);
         }))
      .def("__eq__", &item_wrapper::operator==, pybind11::is_operator())
      .def("__ne__", &item_wrapper::operator!=, pybind11::is_operator())
      .def("name", &item_wrapper::name)
      .def("has_properties", &item_wrapper::has_properties)
      .def("dim", &item_wrapper::dim)
      .def("size",&item_wrapper::size)
      .def("features", &item_wrapper::features)
      .def("times", &item_wrapper::times)
      .def("properties", &item_wrapper::properties)
      .def("properties_contains", &item_wrapper::properties_contains)
      .def("properties_erase", &item_wrapper::erase_properties)
      .def("properties_set", &item_wrapper::set_properties)
      ;
}
