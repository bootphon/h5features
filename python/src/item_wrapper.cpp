#include "item_wrapper.h"


// prepare cast for h5features::properties
namespace pybind11::detail
{
template <>
struct type_caster<h5features::properties>
{
   PYBIND11_TYPE_CASTER(h5features::properties, "p");
   bool load(handle src, bool)
   {
      for(const auto& item: src)
         value.set(item.cast<std::string>(), src[item].cast<h5features::properties::value_type>());
      return true;
   }
};


// prepare cast for h5features::properties
template <>
struct type_caster<h5features::properties::value_type>
{
   PYBIND11_TYPE_CASTER(h5features::properties::value_type, "pvt");
   bool load(handle src, bool)
   {
      PyObject* pyob = src.ptr();
      if (isinstance<pybind11::bool_>(src))
      {
         value = handle(pyob).cast<bool>();
      }
      else if (isinstance<pybind11::int_>(src))
      {
         value = handle(pyob).cast<int>();
      }
      else if (isinstance<pybind11::float_>(src))
      {
         value = handle(pyob).cast<double>();
      }
      else if (isinstance<pybind11::str>(src))
      {
         value = handle(pyob).cast<std::string>();
      }
      else if (isinstance<pybind11::list>(src))
      {
         if (isinstance<pybind11::str>(*src.begin()))
         {
            value = handle(pyob).cast<std::vector<std::string>>();
         }
         else if (isinstance<pybind11::int_>(*src.begin()))
         {
            value = handle(pyob).cast<std::vector<int>>();
         }
         else if (isinstance<pybind11::float_>(*src.begin()))
         {
            value = handle(pyob).cast<std::vector<double>>();
         }
      }
      else if (isinstance<pybind11::dict>(src))
      {
         value = handle(pyob).cast<h5features::properties>();
      }
      return true;
   }
};
}


template <typename String>
inline pybind11::str decode(const String& string)
{
   return pybind11::str(PyUnicode_DecodeUTF8(string.data(), string.length(), NULL));
}


pybind11::dict return_props(const h5features::properties& src)
{
   pybind11::dict to_return;
   for(const auto& item : src)
   {
      if (item.second.type() == typeid(int))
      {
         to_return[decode(item.first)] = pybind11::int_(boost::get<int>(item.second));
      }
      else if (item.second.type() == typeid(bool))
      {
         to_return[decode(item.first)] = pybind11::bool_(boost::get<bool>(item.second));
      }
      else if (item.second.type() == typeid(double))
      {
         to_return[decode(item.first)] = pybind11::float_(boost::get<double>(item.second));
      }
      else if (item.second.type() == typeid(std::string))
      {
         to_return[decode(item.first)] = decode(boost::get<std::string>(item.second));
      }
      else if (item.second.type() == typeid(std::vector<int>))
      {
         to_return[decode(item.first)] = pybind11::cast(boost::get<std::vector<int>>(item.second));
      }
      else if (item.second.type() == typeid(std::vector<double>))
      {
         to_return[decode(item.first)] = pybind11::cast(boost::get<std::vector<double>>(item.second));
      }
      else if (item.second.type() == typeid(std::vector<std::string>))
      {
         to_return[decode(item.first)] = pybind11::cast(boost::get<std::vector<std::string>>(item.second));
      }
      else if (item.second.type() == typeid(h5features::properties))
      {
         to_return[decode(item.first)] = return_props(boost::get<h5features::properties>(item.second));
      }
   }
   return to_return;
}


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

   // create properties object
   auto props = pybind11::handle(properties).cast<h5features::properties>();

   // instanciate item object
   return item_wrapper(name, cfeatures, ctimes, props, check);
}


item_wrapper::item_wrapper(h5features::item&& item)
   : h5features::item(std::move(item))
{}


pybind11::dict item_wrapper::properties() const
{
   return return_props(h5features::item::properties());
}


pybind11::array_t<double> item_wrapper::features() const
{
   const auto& features = h5features::item::features();
   double* p = (double*)features.data().data();
   auto array = pybind11::array_t<double>(
      {features.size(), features.dim()}, p,
      pybind11::capsule(new auto(p), [](void* ptr){ delete reinterpret_cast<decltype(p)*>(ptr);}));
   // // make the array read-only
   // reinterpret_cast<pybind11::detail::PyArray_Proxy*>(
   //    array.ptr())->flags &= ~pybind11::detail::npy_api::NPY_ARRAY_WRITEABLE_;
   return array;
}


pybind11::array_t<double> item_wrapper::times() const
{
   const auto& times = h5features::item::times();
   double* p=(double*)times.data().data();
   auto array = pybind11::array_t<double>(
      {times.size(), times.dim()}, p,
      pybind11::capsule(new auto(p), [](void* ptr){ delete reinterpret_cast<decltype(p)*>(ptr);}));
   // // make the array read-only
   // reinterpret_cast<pybind11::detail::PyArray_Proxy*>(
   //    array.ptr())->flags &= ~pybind11::detail::npy_api::NPY_ARRAY_WRITEABLE_;
   return array;
}
