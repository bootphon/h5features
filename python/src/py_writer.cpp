#include <pybind11/pybind11.h>
#include <h5features/writer.h>
#include <h5features/version.h>
#include "item_wrapper.h"


class writer_wrapper : public h5features::writer
{
public:
   using h5features::writer::writer;

   void write(item_wrapper item)
   {
      h5features::writer::write(item);
   }
};


void init_writer(pybind11::module& m)
{
   pybind11::class_<writer_wrapper> writer(m, "WriterWrapper");

   writer.def(pybind11::init([](
         const std::string& filename,
         const std::string& group = "features",
         bool overwrite= false,
         bool compress = true,
         h5features::version version=h5features::current_version)
         {
            return writer_wrapper(filename, group, overwrite, compress, version);
         }));

   writer.def("write", &writer_wrapper::write);
   writer.def("version", &writer_wrapper::version);
   writer.def("filename", &writer_wrapper::filename);
   writer.def("groupname", &writer_wrapper::groupname);
}
