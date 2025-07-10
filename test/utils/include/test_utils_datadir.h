#ifndef H5FEATURES_TEST_UTILS_DATADIR_H
#define H5FEATURES_TEST_UTILS_DATADIR_H

#include <string>
#include <vector>

namespace utils {
namespace fixture {
struct data_directory {
  data_directory();
  ~data_directory();

  // the directory containing test files
  std::string data_dir;

  // the test files as absolute paths
  std::vector<std::string> data_files;
};
} // namespace fixture
} // namespace utils

#endif // H5FEATURES_TEST_UTILS_DATADIR_H
