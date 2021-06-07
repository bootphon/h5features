#include <h5features/reader.h>
#include <item.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace pybind
{
class reader : h5features::reader
{
public:
   // constructor
   reader(const std::string& filename,const std::string& group);

   // returns list of item in file and group read
   pybind11::list items();

   // read an item in file/group
   pybind::item read(const std::string& name, bool ignore_properties);

   // read an item in file/group from t1 to tn time
   pybind::item read_btw(const std::string& name, double start, double stop, bool ignore_properties);

   // return filename
   std::string filename();

   // return groupname
   std::string groupname();

   // return version used
   h5features::version get_version();
};
}
