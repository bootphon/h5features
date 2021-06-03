#include  <item.h>

pybind11::dict return_props(h5features::properties src);

pybind::item::item(const std::string& name,
            const h5features::features& features,
            const h5features::times& times,
            const h5features::properties& properties,
            bool check) : h5features::item::item(name, features, times, properties, check)
{
   
}
pybind::item::item(h5features::item item) : pybind::item(item.name(), item.features(), item.times(), item.properties(), true)
{
   
}

std::string pybind::item::name()  {return h5features::item::name(); }
bool pybind::item::has_properties()  {return h5features::item::has_properties();} 
double pybind::item::dim()  {return h5features::item::dim();} 
double pybind::item::size() {return h5features::item::size();} 
bool pybind::item::operator==(const pybind::item& other) const noexcept {return h5features::item::operator==(other);} 
         /// Returns true if the two items are not equal
bool pybind::item::operator!=(const pybind::item& other) const noexcept {return h5features::item::operator!=(other);} 

bool pybind::item::properties_contains(const std::string& name)
{
   /* check if properties exists*/
   return h5features::item::properties().contains(name);
}
void pybind::item::erase_properties(const std::string& name)
{
   /*delete a propertie*/
   h5features::properties& ref = const_cast <h5features::properties&>(h5features::item::properties());
   ref.erase(name);
}


void pybind::item::set_properties(const std::string& name, pybind11::handle src)
{
   /* parse properties from python*/
   PyObject* pyob = src.ptr();
      if (pybind11::isinstance<pybind11::bool_>(src)){
         
         bool value = pybind11::handle(pyob).cast<bool>();
         h5features::properties& ref = const_cast <h5features::properties&>(h5features::item::properties());
         ref.set<decltype(value)>(name, value);
      }
      else if (pybind11::isinstance<pybind11::int_>(src)){
         
         int value = pybind11::handle(pyob).cast<int>();
         h5features::properties& ref = const_cast <h5features::properties&>(h5features::item::properties());
         ref.set<decltype(value)>(name, value);
      }
      else if (pybind11::isinstance<pybind11::float_>(src)){
         double value = pybind11::handle(pyob).cast<double>();
         h5features::properties& ref = const_cast <h5features::properties&>(h5features::item::properties());
         ref.set<decltype(value)>(name, value);
      }
      else if (pybind11::isinstance<pybind11::str>(src)){
         std::string value = pybind11::handle(pyob).cast<std::string>();
         h5features::properties& ref = const_cast <h5features::properties&>(h5features::item::properties());
         ref.set<decltype(value)>(name, value);
      }
      else if (pybind11::isinstance<pybind11::list>(src)){
         if (pybind11::isinstance<pybind11::str>(*src.begin())) {
            std::vector<std::string> value = pybind11::handle(pyob).cast<std::vector<std::string>>();
            h5features::properties& ref = const_cast <h5features::properties&>(h5features::item::properties());
            ref.set<decltype(value)>(name, value);
         }
         else if (pybind11::isinstance<pybind11::int_>(*src.begin())) {
            std::vector<int> value = pybind11::handle(pyob).cast<std::vector<int>>();
            h5features::properties& ref = const_cast <h5features::properties&>(h5features::item::properties());
            ref.set<decltype(value)>(name, value);
         }
         else if (pybind11::isinstance<pybind11::float_>(*src.begin())) {
            std::vector<double> value = pybind11::handle(pyob).cast<std::vector<double>>();
            h5features::properties& ref = const_cast <h5features::properties&>(h5features::item::properties());
            ref.set<decltype(value)>(name, value);
         }
      }
      else if (pybind11::isinstance<pybind11::dict>(src)){ 

         h5features::properties value = pybind11::handle(pyob).cast<h5features::properties>();
         h5features::properties& ref = const_cast <h5features::properties&>(h5features::item::properties());
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


pybind11::dict pybind::item::properties()
{
   /* return properties */
   auto src = h5features::item::properties();
   return return_props(src);
}

pybind11::array_t<double> pybind::item::features()
{

   /*
   return features
   */
   double* p=(double*)h5features::item::features().data().data();
         return  pybind11::array_t<double>(
            {h5features::item::features().size(),h5features::item::features().dim()}, p
            , 
            pybind11::capsule(
        new auto(p)
        ,
        [](void* ptr){ delete reinterpret_cast<decltype(p)*>(ptr); }
    )
    );
}

pybind11::array_t<double> pybind::item::times()
{
   /*
   return an array of time with row, the number of times, and columns, the start and end of time
   */
   double* p=(double*)h5features::item::times().data().data();
         return  pybind11::array_t<double>(
            {h5features::item::times().size(),h5features::item::times().dim()}, p
            , pybind11::capsule(
        new auto(p),
        [](void* ptr){ delete reinterpret_cast<decltype(p)*>(ptr); }
    )
    );
}