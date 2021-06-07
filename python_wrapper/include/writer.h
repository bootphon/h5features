#include <h5features/writer.h>
#include <pybind11/pybind11.h>
#include <h5features/version.h>
#include <item.h>
namespace pybind
{
    class writer : public h5features::writer
    {
        public:
            // constructor
            writer(
            const std::string& filename,
            const std::string& group = "features",
            bool overwrite= false,
            bool compress = true,
            h5features::version version=h5features::current_version
            );

            // write an item
            void write(pybind::item item);

            /// Returns the h5features format version being writen
            h5features::version get_version();

            /// Returns the HDF5 file name
            std::string filename();

            /// Returns the HDF5 group name
            std::string groupname();
    };
}