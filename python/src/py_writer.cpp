#include <pybind11/pybind11.h>
#include <h5features/writer.h>
#include <h5features/version.h>
#include "item_wrapper.h"



class writer_wrapper : public h5features::writer
{
public:
   using h5features::writer::writer;

   void write(pybind::item item)
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
         h5features::version version=h5features::current_version
         ) {
            // auto start = std::chrono::high_resolution_clock::now();
            // auto wt =  h5features::writer(filename, group, overwrite, compress, version);
            // auto finish = std::chrono::high_resolution_clock::now();
            // std::chrono::duration<double> elapsed = finish - start;
            // std::cout << "Elapsed time writer: " << elapsed.count() << " s\n";
            // return wt;
            return writer_wrapper(filename, group, overwrite, compress, version);
         }));

   writer.def("write", &writer_wrapper::write, "write item");
   writer.def("get_version", &writer_wrapper::version, "return version");
   writer.def("filename", &writer_wrapper::filename, "return filename");
   writer.def("groupname", &writer_wrapper::groupname, "return groupname");

   pybind11::enum_<h5features::version>(writer, "version")
      .value("v1_0", h5features::version::v1_0)
      .value("v1_1", h5features::version::v1_1)
      .value("v1_2", h5features::version::v1_2)
      .value("v2_0", h5features::version::v2_0)
      .export_values();
}
