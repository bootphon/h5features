#include <pbreader.h>
#include <pybind11/pybind11.h>

void init_reader(pybind11::module& m)
{
   pybind11::class_<pbreader> reader(m, "Reader");


   reader.def(pybind11::init([](
         const std::string& filename,
         const std::string& group
         ) {

            // auto start = std::chrono::high_resolution_clock::now();
            // auto rd =  h5features::reader(filename, group);
            // auto finish = std::chrono::high_resolution_clock::now();
            // std::chrono::duration<double> elapsed = finish - start;
            // std::cout << "Elapsed time reader: " << elapsed.count() << " s\n";
            // return rd;
            return pbreader(filename, group);
         }));
            
      reader.def("read", &pbreader::read, "read item");
      reader.def("read_btw", &pbreader::read_btw, "read item between times");
      reader.def("items", &pbreader::items, "return items");
      reader.def("filename", &pbreader::filename, "Returns the name of the file being read");
      reader.def("groupname", &pbreader::groupname, "Returns the name of the group being read in the file");
      // reader.def("version", &h5features::reader::version, "Returns the version of the h5features data in the group");
      reader.def("get_version", &pbreader::get_version,"Returns the version of the h5features data in the group");
   //    pybind11::enum_<h5features::version>(reader, "rversion")
   //    .value("v1_0", h5features::version::v1_0)
   //  .value("v1_1", h5features::version::v1_1)
   //    .value("v1_2", h5features::version::v1_2)
   //    .value("v2_0", h5features::version::v2_0)
   //    .export_values();
}
