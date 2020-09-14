#ifndef H5FEATURES_TEST_UTILS_DATADIR_H
#define H5FEATURES_TEST_UTILS_DATADIR_H

#include <string>
#include <vector>


namespace utils
{
// the directory containing test files
extern const std::string data_directory;

// the test files as absolute paths
std::vector<std::string> data_files();
}


#endif  // H5FEATURES_TEST_UTILS_DATADIR_H
