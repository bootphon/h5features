#include "item_wrapper.h"


item_wrapper::item_wrapper(
   const std::string& name,
   const h5features::features& features,
   const h5features::times& times,
   const h5features::properties& properties,
   bool check)
   : h5features::item::item(name, features, times, properties, check)
{}


item_wrapper::item_wrapper(const h5features::item& item)
   : item_wrapper(item.name(), item.features(), item.times(), item.properties(), true)
{}


std::string item_wrapper::name()
{
   return h5features::item::name();
}


bool item_wrapper::has_properties()
{
   return h5features::item::has_properties();
}


std::size_t item_wrapper::dim()
{
   return h5features::item::dim();
}


std::size_t item_wrapper::size()
{
   return h5features::item::size();
}


bool item_wrapper::operator==(const item_wrapper& other) const noexcept
{
   return h5features::item::operator==(other);
}


bool item_wrapper::operator!=(const item_wrapper& other) const noexcept
{
   return h5features::item::operator!=(other);
}


pybind11::dict return_props(h5features::properties src)
{
   /* parse properties type from cpp*/
   pybind11::dict to_return;
   for(const auto& item : src)
   {
      if (item.second.type().name() == typeid(int).name())
      {
         to_return[pybind11::str(
               PyUnicode_DecodeUTF8(item.first.data(), item.first.length(), NULL))] =
            pybind11::int_(boost::get<int>(item.second));
      }
      else if (item.second.type().name() == typeid(bool).name())
      {
         to_return[pybind11::str(
               PyUnicode_DecodeUTF8(item.first.data(), item.first.length(), NULL))] =
            pybind11::bool_(boost::get<bool>(item.second));
      }
      else if (item.second.type().name() == typeid(double).name())
      {
         to_return[pybind11::str(
               PyUnicode_DecodeUTF8(item.first.data(), item.first.length(), NULL))] =
            pybind11::float_(boost::get<double>(item.second));
      }
      else if (item.second.type().name() == typeid(std::string).name())
      {
         std::string str = boost::get<std::string>(item.second);
         to_return[pybind11::str(
               PyUnicode_DecodeUTF8(item.first.data(), item.first.length(), NULL))] =
            pybind11::str(PyUnicode_DecodeUTF8(str.data(), str.length(), NULL));
      }
      else if (item.second.type() == typeid(std::vector<int>))
      {
         to_return[pybind11::str(
               PyUnicode_DecodeUTF8(item.first.data(), item.first.length(), NULL))] =
            pybind11::cast(boost::get<std::vector<int>>(item.second));
      }
      else if (item.second.type() == typeid(std::vector<double>))
      {
         to_return[pybind11::str(
               PyUnicode_DecodeUTF8(item.first.data(), item.first.length(), NULL))] =
            pybind11::cast(boost::get<std::vector<double>>(item.second));
      }
      else if (item.second.type() == typeid(std::vector<std::string>))
      {
         to_return[pybind11::str(
               PyUnicode_DecodeUTF8(item.first.data(), item.first.length(), NULL))] =
            pybind11::cast(boost::get<std::vector<std::string>>(item.second));
      }
      else if (item.second.type() == typeid(h5features::properties))
      {
         to_return[pybind11::str(
               PyUnicode_DecodeUTF8(item.first.data(), item.first.length(), NULL))] =
            return_props(boost::get<h5features::properties>(item.second));
      }
   }
   return to_return;
}


pybind11::dict item_wrapper::properties()
{
   return return_props(h5features::item::properties());
}


pybind11::array_t<double> item_wrapper::features()
{
   const auto& features = h5features::item::features();
   double* p = (double*)features.data().data();
   return  pybind11::array_t<double>(
      {features.size(), features.dim()}, p,
      pybind11::capsule(new auto(p), [](void* ptr){ delete reinterpret_cast<decltype(p)*>(ptr); }));
}


pybind11::array_t<double> item_wrapper::times()
{
   const auto& times = h5features::item::times();
   double* p=(double*)times.data().data();
   return  pybind11::array_t<double>(
      {times.size(), times.dim()}, p,
      pybind11::capsule(new auto(p), [](void* ptr){ delete reinterpret_cast<decltype(p)*>(ptr); }));
}
