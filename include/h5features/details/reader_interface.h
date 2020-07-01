#ifndef H5FEATURES_READER_INTERFACE_H
#define H5FEATURES_READER_INTERFACE_H

#include <h5features/hdf5.h>
#include <h5features/item.h>
#include <h5features/version.h>
#include <string>
#include <vector>


namespace h5features
{
namespace details
{
class reader_interface
{
public:
   reader_interface(hdf5::Group&& group, h5features::version version);

   h5features::version version() const noexcept;

   virtual std::vector<std::string> items() const = 0;

   virtual h5features::item read_item(
      const std::string& name, bool ignore_properties=false) const = 0;

   virtual h5features::item read_item(
      const std::string& name, double start, double stop, bool ignore_properties=false) const = 0;

protected:
   // The underlying HDF5 group to read from
   const hdf5::Group m_group;

   // The h5features file version
   h5features::version m_version;
};
}
}

#endif  // H5FEATURES_READER_INTERFACE_H
