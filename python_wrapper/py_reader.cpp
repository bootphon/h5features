#include <h5features/reader.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
h5features::item h5features::reader::pbind_read(const std::string& name, bool ignore_properties=false)
{
   return this->read_item(name, ignore_properties=ignore_properties);
}
h5features::item h5features::reader::pbind_read_btw(const std::string& name, double start, double stop, bool ignore_properties=false)
{
   return this->read_item(name, start, stop, ignore_properties=ignore_properties);
}
template<class T>
T h5features::reader::pbind_items()
{
   return pybind11::cast(this->items());
}

void init_reader(pybind11::module& m)
{
   pybind11::class_<h5features::reader> reader(m, "Reader");


   reader.def(pybind11::init([](
         const std::string& filename,
         const std::string& group
         ) {
            return h5features::reader(filename, group);
         }));
            
      reader.def("read", &h5features::reader::pbind_read, "read item");
      reader.def("read_btw", &h5features::reader::pbind_read_btw, "read item between times");
      reader.def("items", &h5features::reader::pbind_items<pybind11::list>, "return items");
      reader.def("filename", &h5features::reader::filename, "Returns the name of the file being read");
      reader.def("groupname", &h5features::reader::groupname, "Returns the name of the group being read in the file");
      // reader.def("version", &h5features::reader::version, "Returns the version of the h5features data in the group");
      reader.def("get_version", &h5features::reader::version,"Returns the version of the h5features data in the group");
   //    pybind11::enum_<h5features::version>(reader, "rversion")
   //    .value("v1_0", h5features::version::v1_0)
   //  .value("v1_1", h5features::version::v1_1)
   //    .value("v1_2", h5features::version::v1_2)
   //    .value("v2_0", h5features::version::v2_0)
   //    .export_values();
}
