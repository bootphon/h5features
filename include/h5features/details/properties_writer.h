#ifndef H5FEATURES_PROPERTIES_WRITER_H
#define H5FEATURES_PROPERTIES_WRITER_H

#include "h5features/hdf5.h"
#include "h5features/properties.h"

namespace h5features {
namespace details {

/**
   Write a property to a given HDF5 group

   Internally the scalar properties (bool, int, double and string) are stored as
   attribute within the HDF5 group. The vector properties are stored as dataset
   (optionally compressed).

   \param properties The properties to write as HDF5
   \param group The HDF5 group to write the properties to. The group must be
   existing and empty.
   \param compress When true, compress the properties datasets

   \throw h5features::exception If the `group` is not empty.

*/
void write_properties(const h5features::properties &properties, hdf5::Group &group, bool compress);
} // namespace details
} // namespace h5features

#endif // H5FEATURES_PROPERTIES_WRITER_H
