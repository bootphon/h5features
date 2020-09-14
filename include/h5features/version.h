#ifndef H5FEATURES_VERSION_H
#define H5FEATURES_VERSION_H

#include <h5features/hdf5.h>
#include <iostream>


namespace h5features
{
/// The different h5features format versions
enum class version{v1_0, v1_1, v1_2, v2_0};

/// Returns the current (latest) version
constexpr version current_version = version::v2_0;


/**
   \brief Returns the version read from a given HDF5 `group`

   Look for a "version" attribute in the `group` and return its value.

   \param group The HDF5 group to read version from

   \throw h5features::exception If the "version" attribute is not found or if it
   is not a valid h5features file format version.

*/
version read_version(const hdf5::Group& group);

/**
   \brief Writes the `version` to a HDF5 `group`

   Writes to the "version" attribute of the group, create the attribute if
   non-existing, overwrite otherwise. The attribute is wrote as a string in the
   HDF5 file.

 */
void write_version(hdf5::Group& group, h5features::version version);


/// Send a version number to stream
std::ostream& operator<<(std::ostream& os, h5features::version v);
}

#endif  // H5FEATURES_VERSION_H
