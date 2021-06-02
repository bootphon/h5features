#include  <pbitem.h>

pybind11::dict return_props(h5features::properties src);

pbitem::pbitem(const std::string& name,
            const h5features::features& features,
            const h5features::times& times,
            const h5features::properties& properties,
            bool check) : item::item(name, features, times, properties, check)
{
   
}
pbitem::pbitem(h5features::item item) : pbitem(item.name(), item.features(), item.times(), item.properties(), true)
{
   
}

std::string pbitem::name()  {return item::name(); }
bool pbitem::has_properties()  {return item::has_properties();} 
double pbitem::dim()  {return item::dim();} 
double pbitem::size() {return item::size();} 
bool pbitem::operator==(const pbitem& other) const noexcept {return item::operator==(other);} 
         /// Returns true if the two items are not equal
bool pbitem::operator!=(const pbitem& other) const noexcept {return item::operator!=(other);} 

bool pbitem::properties_contains(const std::string& name)
{
   /* check if properties exists*/
   return item::properties().contains(name);
}
void pbitem::erase_properties(const std::string& name)
{
   /*delete a propertie*/
   h5features::properties& ref = const_cast <h5features::properties&>(item::properties());
   ref.erase(name);
}


void pbitem::set_properties(const std::string& name, pybind11::handle src)
{
   /* parse properties from python*/
   PyObject* pyob = src.ptr();
      if (pybind11::isinstance<pybind11::bool_>(src)){
         
         bool value = pybind11::handle(pyob).cast<bool>();
         h5features::properties& ref = const_cast <h5features::properties&>(item::properties());
         ref.set<decltype(value)>(name, value);
      }
      else if (pybind11::isinstance<pybind11::int_>(src)){
         
         int value = pybind11::handle(pyob).cast<int>();
         h5features::properties& ref = const_cast <h5features::properties&>(item::properties());
         ref.set<decltype(value)>(name, value);
      }
      else if (pybind11::isinstance<pybind11::float_>(src)){
         double value = pybind11::handle(pyob).cast<double>();
         h5features::properties& ref = const_cast <h5features::properties&>(item::properties());
         ref.set<decltype(value)>(name, value);
      }
      else if (pybind11::isinstance<pybind11::str>(src)){
         std::string value = pybind11::handle(pyob).cast<std::string>();
         h5features::properties& ref = const_cast <h5features::properties&>(item::properties());
         ref.set<decltype(value)>(name, value);
      }
      else if (pybind11::isinstance<pybind11::list>(src)){
         if (pybind11::isinstance<pybind11::str>(*src.begin())) {
            std::vector<std::string> value = pybind11::handle(pyob).cast<std::vector<std::string>>();
            h5features::properties& ref = const_cast <h5features::properties&>(item::properties());
            ref.set<decltype(value)>(name, value);
         }
         else if (pybind11::isinstance<pybind11::int_>(*src.begin())) {
            std::vector<int> value = pybind11::handle(pyob).cast<std::vector<int>>();
            h5features::properties& ref = const_cast <h5features::properties&>(item::properties());
            ref.set<decltype(value)>(name, value);
         }
         else if (pybind11::isinstance<pybind11::float_>(*src.begin())) {
            std::vector<double> value = pybind11::handle(pyob).cast<std::vector<double>>();
            h5features::properties& ref = const_cast <h5features::properties&>(item::properties());
            ref.set<decltype(value)>(name, value);
         }
      }
      else if (pybind11::isinstance<pybind11::dict>(src)){ 

         h5features::properties value = pybind11::handle(pyob).cast<h5features::properties>();
         h5features::properties& ref = const_cast <h5features::properties&>(item::properties());
         ref.set<decltype(value)>(name, value);
   }
   
}


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


pybind11::dict pbitem::properties()
{
   /* return properties */
   auto src = item::properties();
   return return_props(src);
}

pybind11::array_t<double> pbitem::features()
{

   /*
   return features
   */
   double* p=(double*)item::features().data().data();
         return  pybind11::array_t<double>(
            {item::features().size(),item::features().dim()}, p
            , 
            pybind11::capsule(
        new auto(p)
        ,
        [](void* ptr){ delete reinterpret_cast<decltype(p)*>(ptr); }
    )
    );
}

pybind11::array_t<double> pbitem::times()
{
   /*
   return an array of time with row, the number of times, and columns, the start and end of time
   */
   double* p=(double*)item::times().data().data();
         return  pybind11::array_t<double>(
            {item::times().size(),item::times().dim()}, p
            , pybind11::capsule(
        new auto(p),
        [](void* ptr){ delete reinterpret_cast<decltype(p)*>(ptr); }
    )
    );
}