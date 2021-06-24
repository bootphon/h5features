#include <pybind11/pybind11.h>
#include "item_wrapper.h"
#include "properties_wrapper.h"


item_wrapper item_wrapper::create(
   const std::string& name,
   const pybind11::array_t<double, pybind11::array::c_style | pybind11::array::forcecast>& features,
   const pybind11::array_t<double, pybind11::array::c_style | pybind11::array::forcecast>& times,
   const pybind11::dict& properties,
   bool check)
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

   // instanciate item object
   return item_wrapper(
      name,
      cfeatures,
      ctimes,
      properties_wrapper(properties),
      check);
}


item_wrapper::item_wrapper(h5features::item&& item)
   : h5features::item(std::move(item))
{}


template<class T>
inline pybind11::array_t<double> wrap_to_array(const T& src, bool readonly=false)
{
   double* p = (double*)src.data().data();
   auto array = pybind11::array_t<double>(
      {src.size(), src.dim()}, p,
      pybind11::capsule(new auto(p), [](void* ptr){ delete reinterpret_cast<decltype(p)*>(ptr);}));

   if(readonly)
   {
      // make the array read-only
      reinterpret_cast<pybind11::detail::PyArray_Proxy*>(
         array.ptr())->flags &= ~pybind11::detail::npy_api::NPY_ARRAY_WRITEABLE_;
   }

   return array;
}

pybind11::array_t<double> item_wrapper::features() const
{
   return wrap_to_array(h5features::item::features(), true);
}


pybind11::array_t<double> item_wrapper::times() const
{
   return wrap_to_array(h5features::item::times(), true);
}


pybind11::dict item_wrapper::properties() const
{
   return static_cast<properties_wrapper>(h5features::item::properties()).py_todict();
}


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
