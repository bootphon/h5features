#ifndef H5FEATURES_V2_READER_H
#define H5FEATURES_V2_READER_H

#include <h5features/hdf5.h>
#include <h5features/item.h>
#include <h5features/version.h>
#include <h5features/details/reader_interface.h>
#include <string>
#include <vector>


namespace h5features
{
namespace v2
{
class reader : public h5features::details::reader_interface
{
public:
   reader(hdf5::Group&& group, h5features::version version);

   std::vector<std::string> items() const override;

   h5features::item read_item(
      const std::string& name, bool ignore_properties) const override;

   h5features::item read_item(
      const std::string& name, double start, double stop, bool ignore_properties) const override;

private:
   // Initialize the group, forwarding hdf5::Exception to h5features::exception
   static hdf5::Group init_group(const std::string& filename, const std::string& group);
};
}
}


#endif  // H5FEATURES_V2_READER_H
