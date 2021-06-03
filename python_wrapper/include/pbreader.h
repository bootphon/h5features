#include <h5features/reader.h>
#include <pbitem.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

class pbreader : h5features::reader
{
    public:
        pbreader(const std::string& filename,const std::string& group);
        pybind11::list items();
        pybind::item read(const std::string& name, bool ignore_properties);
        pybind::item read_btw(const std::string& name, double start, double stop, bool ignore_properties);
        std::string filename();
        std::string groupname();
        h5features::version get_version();
};