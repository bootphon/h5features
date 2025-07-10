#ifndef H5FEATURES_TEST_TMPDIR_H
#define H5FEATURES_TEST_TMPDIR_H

#include "boost/filesystem.hpp"

namespace utils {
namespace fixture {
// A fixture to create and delete a temporary directory
struct temp_directory {
  temp_directory();
  ~temp_directory();
  boost::filesystem::path tmpdir;
};
} // namespace fixture
} // namespace utils

#endif // H5FEATURES_TEST_TMPDIR_H
