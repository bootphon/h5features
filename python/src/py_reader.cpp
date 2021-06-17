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
   pybind::item read(const std::string& name, bool ignore_properties)
   {
      return pybind::item(h5features::reader::read_item(name, ignore_properties=ignore_properties));
   }

   // read an item in file/group from t1 to tn time
   pybind::item read_btw(const std::string& name, double start, double stop, bool ignore_properties)
   {
      return pybind::item(h5features::reader::read_item(name, start, stop, ignore_properties=ignore_properties));
   }
};


void init_reader(pybind11::module& m)
{
   pybind11::class_<reader_wrapper> reader(m, "ReaderWrapper");

   reader.def(pybind11::init([](
     const std::string& filename,
     const std::string& group) {return reader_wrapper(filename, group);}));

      reader.def(
         "read", &reader_wrapper::read,
         "read item");

      reader.def(
         "read_btw", &reader_wrapper::read_btw,
         "read item between times");

      reader.def(
         "items", &reader_wrapper::items,
         "return items");

      reader.def(
         "filename", &reader_wrapper::filename,
         "Returns the name of the file being read");

      reader.def(
         "groupname", &reader_wrapper::groupname,
         "Returns the name of the group being read in the file");

      reader.def(
         "get_version", &reader_wrapper::version,
         "Returns the version of the h5features data in the group");
}
