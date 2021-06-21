#include <pybind11/pybind11.h>
#include "item_wrapper.h"


void init_item(pybind11::module& m)
{
   pybind11::class_<item_wrapper>(m, "ItemWrapper")
      .def(pybind11::init(&item_wrapper::create))
      .def("__eq__", &item_wrapper::operator==, pybind11::is_operator())
      .def("__ne__", &item_wrapper::operator!=, pybind11::is_operator())
      .def("name", &item_wrapper::name)
      .def("dim", &item_wrapper::dim)
      .def("size", &item_wrapper::size)
      .def("features", &item_wrapper::features)
      .def("times", &item_wrapper::times)
      .def("properties", &item_wrapper::properties);
}
