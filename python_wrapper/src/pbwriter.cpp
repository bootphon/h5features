#include <pbwriter.h>
// #include <chrono>
pybind11::writer::writer(
        const std::string& filename,
         const std::string& group,
         bool overwrite,
         bool compress,
         h5features::version version
         ) : h5features::writer::writer(filename, group, overwrite, compress, version) {}

h5features::version pybind11::writer::get_version()
{
    return h5features::writer::version();
}

std::string pybind11::writer::filename()
{
    return h5features::writer::filename();
}

std::string pybind11::writer::groupname()
{
    return h5features::writer::groupname();
}

void pybind11::writer::write(pbitem item)
{
   // auto start = std::chrono::high_resolution_clock::now();
   // this->write(item);
   // auto finish = std::chrono::high_resolution_clock::now();
   //          std::chrono::duration<double> elapsed = finish - start;
   //          std::cout << "Elapsed time write: " << elapsed.count() << " s\n";

   h5features::writer::write(item);
}