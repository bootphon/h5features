#ifndef H5FEATURES_PROPERTIES_READER_H
#define H5FEATURES_PROPERTIES_READER_H

#include "h5features/hdf5.h"
#include "h5features/properties.h"

namespace h5features {
namespace details {
/**
   Read properties from a given HDF5 group
 */
h5features::properties read_properties(const hdf5::Group &group);
} // namespace details
} // namespace h5features

#endif // H5FEATURES_PROPERTIES_READER_H
