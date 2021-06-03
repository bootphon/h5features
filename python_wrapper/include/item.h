#include <h5features/item.h>
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include <unordered_map>
#include <iostream>
#include <boost/variant.hpp>
#include <variant>
#include <typeinfo> 

#include <pybind11/embed.h>

namespace pybind
{
   class item: public h5features::item
   {
      public:
            item(
               const std::string& name,
               const h5features::features& features,
               const h5features::times& times,
               const h5features::properties& properties={},
               bool check=true
            );
            item(h5features::item item);
            std::string name();
            bool has_properties();
            double dim();
            double size();
            pybind11::array_t<double> features();
            pybind11::array_t<double> times();
            pybind11::dict properties();
            bool properties_contains(const std::string& name);
            void erase_properties(const std::string& name);
            void set_properties(const std::string& name, pybind11::handle src);
            /// Returns true if the two items are  equal
            bool operator==(const pybind::item& other) const noexcept;
            /// Returns true if the two items are not equal
            bool operator!=(const pybind::item& other) const noexcept;
   };
}
namespace pybind11::detail {
      template <>
   struct type_caster<h5features::properties>  { 
      PYBIND11_TYPE_CASTER(h5features::properties, "p");
     bool load(handle src, bool){
         for (auto item: src)
               value.set(item.cast<std::string>(), src[item].cast<h5features::properties::value_type>());
         return true;
      }};
   template <>
   struct type_caster<h5features::properties::value_type> {
      PYBIND11_TYPE_CASTER(h5features::properties::value_type, "pvt");
      bool load(handle src, bool) {
         PyObject* pyob = src.ptr();
         if (isinstance<pybind11::bool_>(src)){
            
            value = handle(pyob).cast<bool>();
         }
         else if (isinstance<pybind11::int_>(src)){
            
            value = handle(pyob).cast<int>();
         }
         else if (isinstance<pybind11::float_>(src)){
            value = handle(pyob).cast<double>();
         }
         else if (isinstance<pybind11::str>(src)){
            value = handle(pyob).cast<std::string>();
         }
         else if (isinstance<pybind11::list>(src)){
            if (isinstance<pybind11::str>(*src.begin())) {
               value = handle(pyob).cast<std::vector<std::string>>();
            }
            else if (isinstance<pybind11::int_>(*src.begin())) {
               value = handle(pyob).cast<std::vector<int>>();
            }
            else if (isinstance<pybind11::float_>(*src.begin())) {
               value = handle(pyob).cast<std::vector<double>>();
            }
         }
         else if (isinstance<pybind11::dict>(src)){ 

            value = handle(pyob).cast<h5features::properties>();
      }
      return true;
   }
   };
}