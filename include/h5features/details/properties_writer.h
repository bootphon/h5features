#ifndef H5FEATURES_PROPERTIES_WRITER_H
#define H5FEATURES_PROPERTIES_WRITER_H

#include <h5features/hdf5.h>
#include <h5features/properties.h>


namespace h5features
{
namespace details
{

/**
   Write a property to a given HDF5 group

   Internally the scalar properties (bool, int, double and string) are stored as
   attribute within the HDF5 group. The vector properties are stored as dataset
   (optionnally compressed).

*/
void write_properties(const h5features::properties& props, hdf5::Group& group, bool compress);
}
}

#endif  // H5FEATURES_PROPERTIES_WRITER_H
