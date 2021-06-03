#include <h5features/writer.h>
#include <pybind11/pybind11.h>
#include <h5features/version.h>
#include <pbitem.h>
namespace pybind
{
    class writer : public h5features::writer
    {
        public:
            /**
             \brief Instanciates a writer

            \param filename The HDF5 file to write on
            \param group The group in the file to write on
            \param overwrite If true erase the file content if it is already existing.
            If false it will append new items to the existing group.
            \param compress When true, compress the data
            \param version The version of the file to write. Version 1.0 is **not
            available** to write, only read.

            \throw h5features::exception When `overwrite` is true, if the `group`
            already exists in the file and the version is not supported. Or if the
            requested `version` is not supported.

            */
            writer(
            const std::string& filename,
            const std::string& group = "features",
            bool overwrite= false,
            bool compress = true,
            h5features::version version=h5features::current_version
            );

            /**
             \brief Writes a `h5features::item` to disk

            \param item The item to write

            \throw h5features::exception If the item name is already an existing
            object in the group or if the write operation failed.

            */
            void write(pybind::item item);

            /// Returns the h5features format version being writen
            h5features::version get_version();

            /// Returns the HDF5 file name
            std::string filename();

            /// Returns the HDF5 group name
            std::string groupname();
    };
}