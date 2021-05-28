#include <h5features/reader.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
h5features::item h5features::reader::pbind_read(const std::string& name)
{
   return this->read_item(name);
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
      reader.def("items", &h5features::reader::pbind_items<pybind11::list>, "return items")
      ;
   //     pybind11::enum_<h5features::version>(reader, "version")
   //    .value("v1_0", h5features::version::v1_0)
   //  .value("v1_1", h5features::version::v1_1)
   //    .value("v1_2", h5features::version::v1_2)
   //    .value("v2_0", h5features::version::v2_0)
   //    .export_values();
}
