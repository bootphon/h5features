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

/* parse types for properties */
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

   // template <>
   // struct type_caster<boost::variant<h5features::properties::value_type>> : variant_caster<boost::variant<h5features::properties::value_type>>{};
   
}

bool h5features::item::pbind_contains(const std::string& name)
{
   /* check if properties exists*/
   return this->properties().contains(name);
}
void h5features::item::pbind_erase(const std::string& name)
{
   /*delete a propertie*/
   h5features::properties& ref = const_cast <h5features::properties&>(this->properties());
   ref.erase(name);
}

template<class T>
void h5features::item::pbind_set_props(const std::string& name, T src)
{
   /* parse properties from python*/
   PyObject* pyob = src.ptr();
      if (pybind11::isinstance<pybind11::bool_>(src)){
         
         bool value = pybind11::handle(pyob).cast<bool>();
         h5features::properties& ref = const_cast <h5features::properties&>(this->properties());
         ref.set<decltype(value)>(name, value);
      }
      else if (pybind11::isinstance<pybind11::int_>(src)){
         
         int value = pybind11::handle(pyob).cast<int>();
         h5features::properties& ref = const_cast <h5features::properties&>(this->properties());
         ref.set<decltype(value)>(name, value);
      }
      else if (pybind11::isinstance<pybind11::float_>(src)){
         double value = pybind11::handle(pyob).cast<double>();
         h5features::properties& ref = const_cast <h5features::properties&>(this->properties());
         ref.set<decltype(value)>(name, value);
      }
      else if (pybind11::isinstance<pybind11::str>(src)){
         std::string value = pybind11::handle(pyob).cast<std::string>();
         h5features::properties& ref = const_cast <h5features::properties&>(this->properties());
         ref.set<decltype(value)>(name, value);
      }
      else if (pybind11::isinstance<pybind11::list>(src)){
         if (pybind11::isinstance<pybind11::str>(*src.begin())) {
            std::vector<std::string> value = pybind11::handle(pyob).cast<std::vector<std::string>>();
            h5features::properties& ref = const_cast <h5features::properties&>(this->properties());
            ref.set<decltype(value)>(name, value);
         }
         else if (pybind11::isinstance<pybind11::int_>(*src.begin())) {
            std::vector<int> value = pybind11::handle(pyob).cast<std::vector<int>>();
            h5features::properties& ref = const_cast <h5features::properties&>(this->properties());
            ref.set<decltype(value)>(name, value);
         }
         else if (pybind11::isinstance<pybind11::float_>(*src.begin())) {
            std::vector<double> value = pybind11::handle(pyob).cast<std::vector<double>>();
            h5features::properties& ref = const_cast <h5features::properties&>(this->properties());
            ref.set<decltype(value)>(name, value);
         }
      }
      else if (pybind11::isinstance<pybind11::dict>(src)){ 

         h5features::properties value = pybind11::handle(pyob).cast<h5features::properties>();
         h5features::properties& ref = const_cast <h5features::properties&>(this->properties());
         ref.set<decltype(value)>(name, value);
   }
   
}
//  std::unordered_map<std::string, h5features::properties::value_type> & h5features::item::pbind_properties()
// {
 
//    return this->m_properties.m_properties;
// }
pybind11::dict return_props(h5features::properties src);
pybind11::dict return_props(h5features::properties src)
{
   /* parse properties type from cpp*/
      pybind11::dict to_return;
      for (auto item : src)
      {
         if (item.second.type().name() == typeid(int).name()){
            to_return[pybind11::str(PyUnicode_DecodeUTF8(item.first.data(), item.first.length(), NULL))] = pybind11::int_(boost::get<int>(item.second));}
         else if (item.second.type().name() == typeid(bool).name())
            to_return[pybind11::str(PyUnicode_DecodeUTF8(item.first.data(), item.first.length(), NULL))] = pybind11::bool_(boost::get<bool>(item.second));
         else if (item.second.type().name() ==typeid(double).name()){
            to_return[pybind11::str(PyUnicode_DecodeUTF8(item.first.data(), item.first.length(), NULL))] = pybind11::float_(boost::get<double>(item.second));
            }
         else if (item.second.type().name() ==typeid(std::string).name()){
            std::string str = boost::get<std::string>(item.second);
            to_return[pybind11::str(PyUnicode_DecodeUTF8(item.first.data(), item.first.length(), NULL))] = pybind11::str(PyUnicode_DecodeUTF8(str.data(), str.length(), NULL));
         }
         else if (item.second.type() ==typeid(std::vector<int>))
            to_return[pybind11::str(PyUnicode_DecodeUTF8(item.first.data(), item.first.length(), NULL))] = pybind11::cast(boost::get<std::vector<int>>(item.second));
         else if (item.second.type() ==typeid(std::vector<double>))
            to_return[pybind11::str(PyUnicode_DecodeUTF8(item.first.data(), item.first.length(), NULL))] = pybind11::cast(boost::get<std::vector<double>>(item.second));
         else if (item.second.type() ==typeid(std::vector<std::string>)) {
            to_return[pybind11::str(PyUnicode_DecodeUTF8(item.first.data(), item.first.length(), NULL))] = pybind11::cast(boost::get<std::vector<std::string>>(item.second));
         }
         else if  (item.second.type() == typeid(h5features::properties)) {
            to_return[pybind11::str(PyUnicode_DecodeUTF8(item.first.data(), item.first.length(), NULL))] = return_props(boost::get<h5features::properties>(item.second));
         }
   }
      return to_return;
}
template <class T>
T h5features::item::pbind_get_properties(const std::string& name)
{
   /* return a properties */
   auto src = this->m_properties;
   auto dict = return_props(src);
   return dict[pybind11::str(name)];
}

template<class T>
T h5features::item::pbind_properties()
{
   /* return properties */
   auto src = this->m_properties;
   return return_props(src);
}
template<class T>
T h5features::item::pbind_features()
{

   /*
   return features
   */
   double* p=(double*)this->features().data().data();
         return  T(
            {this->features().dim(),this->features().size()}, p
            , 
            pybind11::capsule(
        new auto(p)
        ,
        [](void* ptr){ delete reinterpret_cast<decltype(p)*>(ptr); }
    )
    );
}
template<class T>
T h5features::item::pbind_times()
{
   /*
   return an array of time with row, the number of times, and columns, the start and end of time
   */
   double* p=(double*)this->times().data().data();
         return  T(
            {this->times().size(),this->times().dim()}, p
            , pybind11::capsule(
        new auto(p),
        [](void* ptr){ delete reinterpret_cast<decltype(p)*>(ptr); }
    )
    );
}
void init_item(pybind11::module& m)
{
   pybind11::class_<h5features::item>(m, "Item", pybind11::buffer_protocol())
      .def(pybind11::init([](
         const std::string& name,
            const pybind11::buffer & features,
            const pybind11::buffer & begin,
            const pybind11::buffer & end,
            const pybind11::dict & properties,
            bool check = true
         ) {
            // create features object
            pybind11::buffer_info info = features.request();
            double *p = (double*)info.ptr;
            std::size_t size = info.size;
            std::size_t shape= info.shape[0];
            auto  array = std::vector<double>(p, p+size);
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

            // auto props = h5features::properties();
            // create properties object
            auto props = pybind11::handle(properties).cast<h5features::properties>();
            return h5features::item(name, feats, tims, props, check);
         }))
      .def("__eq__", &h5features::item::operator==, pybind11::is_operator(), "returns true if the two items instances are equal")
      .def("__ne__", &h5features::item::operator!=, pybind11::is_operator(), "returns true if the two items instances are not equal")      
      .def("name", &h5features::item::name, "returns the name of the item")
      .def("has_properties", &h5features::item::has_properties, "Returns true if the item has attached properties, false otherwise")
      .def("dim", &h5features::item::dim, "returns the dimension of a feature vector")
      .def("size", &h5features::item::size, "returns the number of features vectors")
      .def("features",&h5features::item::pbind_features<pybind11::array_t<double>>)
      .def("times",&h5features::item::pbind_times<pybind11::array_t<double>>)
      .def("properties", &h5features::item::pbind_properties<pybind11::dict>)
      .def("properties_contains", &h5features::item::pbind_contains)
      .def("properties_erase", &h5features::item::pbind_erase)
      .def("properties_set", &h5features::item::pbind_set_props<const pybind11::handle&>)
      // .def("properties_get", &h5features::item::pbind_get_properties<pybind11::handle>)
      ;
}
