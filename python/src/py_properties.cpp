#include <pybind11/pybind11.h>
#include <pybind11/operators.h>
#include <pybind11/stl.h>
#include <h5features/properties.h>

namespace pybind11::detail
{
// Helper class to cast h5features::properties::value_type between C++ and Python
template <>
struct type_caster<h5features::properties::value_type> : variant_caster<h5features::properties::value_type>
{
   PYBIND11_TYPE_CASTER(h5features::properties::value_type, _("properties_value"));

   // Python -> C++
   bool load(handle src, bool)
   {
      if (isinstance<pybind11::bool_>(src))
      {
         value = src.cast<bool>();
      }
      else if (isinstance<pybind11::int_>(src))
      {
         value = src.cast<int>();
      }
      else if (isinstance<pybind11::float_>(src))
      {
         value = src.cast<double>();
      }
      else if (isinstance<pybind11::str>(src))
      {
         value = src.cast<std::string>();
      }
      else if (isinstance<pybind11::list>(src))
      {
         if (isinstance<pybind11::str>(*src.begin()))
         {
            value = src.cast<std::vector<std::string>>();
         }
         else if (isinstance<pybind11::int_>(*src.begin()))
         {
            value = src.cast<std::vector<int>>();
         }
         else if (isinstance<pybind11::float_>(*src.begin()))
         {
            value = src.cast<std::vector<double>>();
         }
      }
      else if (isinstance<pybind11::dict>(src))
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
}  // namespace pybind11::detail


class properties_wrapper : public h5features::properties
{
public:
   using h5features::properties::properties;

   properties_wrapper(const pybind11::dict& dict)
   {
      for(const auto& [key, value] : dict)
      {
         set(key.cast<std::string>(), value.cast<value_type>());
      }
   }

   pybind11::iterator py_iter() const
   {
      return pybind11::make_key_iterator(begin(), end());
   }

   void py_set(const std::string& key, const pybind11::handle& value)
   {
      set(key, value.cast<value_type>());
   }

   pybind11::object py_get(const std::string& name) const
   {
      return pybind11::cast(m_properties.at(name));
   }

   pybind11::iterator py_keys() const
   {
      return py_iter();
   }

   pybind11::list py_values() const
   {
      pybind11::list list;
      for(const auto& item : m_properties)
      {
         list.append(item.second);
      }
      return list;
   }

   pybind11::iterator py_items() const
   {
      return pybind11::make_iterator(begin(), end());
   }

   pybind11::dict py_todict() const
   {
      pybind11::dict dict;
      for(const auto& [key, value] : m_properties)
      {
         dict[pybind11::str(key)] = value;
      }
      return dict;
   }
};


void init_properties(pybind11::module& m)
{
   pybind11::class_<properties_wrapper>(m, "PropertiesWrapper")
      .def(pybind11::init<const pybind11::dict&>())
      .def(pybind11::init<>())
      .def(pybind11::self == pybind11::self)
      .def(pybind11::self != pybind11::self)
      .def("__len__", &properties_wrapper::size)
      .def("__contains__", &properties_wrapper::contains)
      .def("__iter__", &properties_wrapper::py_iter, pybind11::keep_alive<0, 1>())
      .def("__setitem__", &properties_wrapper::py_set)
      .def("__getitem__", &properties_wrapper::py_get)
      .def("keys", &properties_wrapper::py_keys, pybind11::keep_alive<0, 1>())
      .def("values", &properties_wrapper::py_values)
      .def("items", &properties_wrapper::py_items, pybind11::keep_alive<0, 1>())
      .def("todict", &properties_wrapper::py_todict)
      ;
}
