#include <pbwriter.h>
// #include <chrono>
pbwriter::pbwriter(
        const std::string& filename,
         const std::string& group,
         bool overwrite,
         bool compress,
         h5features::version version
         ) : writer::writer(filename, group, overwrite, compress, version) {}

h5features::version pbwriter::get_version()
{
    return writer::version();
}
void pbwriter::write(pbitem item)
{
   // auto start = std::chrono::high_resolution_clock::now();
   // this->write(item);
   // auto finish = std::chrono::high_resolution_clock::now();
   //          std::chrono::duration<double> elapsed = finish - start;
   //          std::cout << "Elapsed time write: " << elapsed.count() << " s\n";

   writer::write(item);
}