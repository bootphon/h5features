#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <h5features/reader.h>
#include "item_wrapper.h"


class reader_wrapper : public h5features::reader
{
public:
   using h5features::reader::reader;

   // returns list of item in file and group read
   pybind11::list items()
   {
      return pybind11::cast(h5features::reader::items());
   }

   // read an item in file/group
   item_wrapper read(const std::string& name, bool ignore_properties)
   {
      return h5features::reader::read_item(name, ignore_properties=ignore_properties);
   }

   // read an item in file/group from t1 to tn time
   item_wrapper read_btw(const std::string& name, double start, double stop, bool ignore_properties)
   {
      return h5features::reader::read_item(name, start, stop, ignore_properties=ignore_properties);
   }

   std::vector<item_wrapper> read_all(bool ignore_properties)
   {
      std::vector<item_wrapper> all_items;
      for(const auto& item: h5features::reader::items())
      {
         all_items.push_back(read(item, ignore_properties));
      }
      return all_items;
   }
};


void init_reader(pybind11::module& m)
{
   pybind11::class_<reader_wrapper> reader(m, "ReaderWrapper");

   reader.def(pybind11::init([](
     const std::string& filename,
     const std::string& group) {return reader_wrapper(filename, group);}));

   reader.def("read", &reader_wrapper::read);
   reader.def("read_btw", &reader_wrapper::read_btw);
   reader.def("read_all", &reader_wrapper::read_all);
   reader.def("items", &reader_wrapper::items);
   reader.def("filename", &reader_wrapper::filename);
   reader.def("groupname", &reader_wrapper::groupname);
   reader.def("version", &reader_wrapper::version);
}
