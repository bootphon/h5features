#include "test_utils_tmpdir.h"

boost::filesystem::path tmpdir_name() {
  return boost::filesystem::temp_directory_path() / boost::filesystem::unique_path();
}

utils::fixture::temp_directory::temp_directory() : tmpdir{tmpdir_name()} {
  boost::filesystem::create_directory(tmpdir);
}

utils::fixture::temp_directory::~temp_directory() { boost::filesystem::remove_all(tmpdir); }
