#include <pbwriter.h>
#include <pybind11/pybind11.h>
#include <h5features/version.h>
#include <h5features/item.h>

void init_writer(pybind11::module& m)
{
   pybind11::class_<pybind11::writer> writer(m, "Writer");

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
            return pybind11::writer(filename, group, overwrite, compress, version);
         }));
            
      writer.def("write", &pybind11::writer::write, "write item");
      writer.def("get_version", &pybind11::writer::get_version, "return version");
      writer.def("filename", &pybind11::writer::filename, "return filename");
      writer.def("groupname", &pybind11::writer::groupname, "return groupname");
      
      
       pybind11::enum_<h5features::version>(writer, "version")
      .value("v1_0", h5features::version::v1_0)
    .value("v1_1", h5features::version::v1_1)
      .value("v1_2", h5features::version::v1_2)
      .value("v2_0", h5features::version::v2_0)
      .export_values();
}
