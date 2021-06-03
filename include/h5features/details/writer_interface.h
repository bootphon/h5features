#ifndef H5FEATURES_WRITER_INTERFACE_H
#define H5FEATURES_WRITER_INTERFACE_H

#include <h5features/hdf5.h>
#include <h5features/item.h>
#include <h5features/version.h>


namespace h5features
{
namespace details
{
class writer_interface
{
public:
   writer_interface(hdf5::Group&& group, bool compress=true, h5features::version version=h5features::current_version);

   virtual ~writer_interface();

   h5features::version version() const noexcept;

   virtual void write(const h5features::item& item) = 0;

protected:
   // The underlying HDF5 group to write to
   hdf5::Group m_group;

   // true if data is compressed on file
   bool m_compress;

   // The h5features file version
   h5features::version m_version;
};
}
}

#endif  // H5FEATURES_WRITER_INTERFACE_H
