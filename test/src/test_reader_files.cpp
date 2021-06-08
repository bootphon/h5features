#define BOOST_TEST_MODULE test_reader_files

#include <h5features/item.h>
#include <h5features/reader.h>
#include <boost/test/included/unit_test.hpp>

#include "test_utils_datadir.h"


BOOST_FIXTURE_TEST_CASE(test_read_files, utils::fixture::data_directory)
{
   std::vector<std::vector<h5features::item>> data;
   for(const auto& file : data_files)
   {
      h5features::reader reader = h5features::reader(file, "features");
      data.push_back(reader.read_all());
   }

   // make sure all files contains the same data
   BOOST_CHECK(std::equal(data.begin() + 1, data.end(), data.begin()));
}
