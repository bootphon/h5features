#include <pybind11/pybind11.h>
#include "item_wrapper.h"


namespace pybind11::detail
{
// Helper class to cast h5features::properties::value_type between C++ and Python
template <>
struct type_caster<h5features::properties::value_type> //: variant_caster<h5features::properties::value_type>
{
   PYBIND11_TYPE_CASTER(h5features::properties::value_type, _("properties_value"));

   // Python -> C++
   bool load(handle src, bool)
   {
      std::cout << "passed-python"<<std::endl;
      if (isinstance<bool_>(src))
      {
         value = src.cast<bool>();
      }
      else if (isinstance<int_>(src))
      {
         value = src.cast<int>();
      }
      else if (isinstance<float_>(src))
      {
         value = src.cast<double>();
      }
      else if (isinstance<str>(src))
      {
         value = src.cast<std::string>();
      }
      else if (isinstance<list>(src))
      {
         if (isinstance<str>(*src.begin()))
         {
            value = src.cast<std::vector<std::string>>();
         }
         else if (isinstance<int_>(*src.begin()))
         {
            value = src.cast<std::vector<int>>();
         }
         else if (isinstance<float_>(*src.begin()))
         {
            value = src.cast<std::vector<double>>();
         }
         else //if (isinstance<h5features::properties>(*src.begin()))
         {
            std::cout << "passed"<<std::endl;
            value = src.cast<std::vector<h5features::properties>>();
         }
      }
      else if (isinstance<dict>(src))
      {
         value = src.cast<h5features::properties>();
      }
      else
      {
         throw std::runtime_error("invalid property value type");
      }

      return true;
   }

   // C++ -> Python
   static handle cast(const h5features::properties::value_type& src, return_value_policy, handle)
   {
      std::cout << "passed-python"<<std::endl;
      return boost::apply_visitor(variant_caster_visitor{}, src);
   }
};



// Helper class to cast h5features::properties between C++ and Python. This is
// required to deal with nested properties.
template <>
struct type_caster<h5features::properties>
{
   PYBIND11_TYPE_CASTER(h5features::properties, _("properties"));

   // Python -> C++
   bool load(handle src, bool)
   {
      for(auto& item: src)
         value.set(item.cast<std::string>(), src[item].cast<h5features::properties::value_type>());
      return true;
   }

   // C++ -> Python
   static handle cast(const h5features::properties& src, return_value_policy, handle)
   {
      pybind11::dict dict;
      for(const auto& [key, value] : src)
      {
         dict[pybind11::str(key)] = value;
      }
      return dict.release();
   }
};


template <>
struct type_caster<std::vector<h5features::properties>>
{
   
   PYBIND11_TYPE_CASTER(std::vector<h5features::properties>, _("vproperties"));

   // Python -> C++
   bool load(handle src, bool)
   {
      for(auto& item: src)
         value.push_back(item.cast<h5features::properties>());
      return true;
   }

   // C++ -> Python
   static handle cast(const std::vector<h5features::properties>& src, return_value_policy, handle)
   {
      pybind11::list list;
      for(size_t i = 0; i < src.size(); ++i)
      {
         list.append(pybind11::cast(src[i]));
      }
      return list.release();
   }
};


}  // namespace pybind11::detail


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
   std::cout << "passed-python"<<std::endl;
   // instanciate item object
   return item_wrapper(
      name,
      cfeatures,
      ctimes,
      properties.cast<h5features::properties>(),
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
   return pybind11::cast(h5features::item::properties());
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
