#ifndef H5FEATURES_VERSION_H
#define H5FEATURES_VERSION_H

#include <h5features/hdf5.h>
#include <iostream>


namespace h5features
{
/**
   \brief The different h5features format versions

   This is **not** the version of the h5features library but the available
   versions of the underlying file format.

 */
enum class version{v1_0, v1_1, v1_2, v2_0};

/// Returns the current (latest) version
constexpr version current_version = version::v2_0;


/**
   \brief Look for a "version" attribute in the `group` and return its value.

   \throw h5features::exception If the "version" attribute is not found or is
   not valid.

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
