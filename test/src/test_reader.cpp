#define BOOST_TEST_MODULE test_reader

#include <h5features/exception.h>
#include <h5features/version.h>
#include <h5features/reader.h>
#include <h5features/writer.h>
#include <boost/test/included/unit_test.hpp>
#include <boost/test/data/test_case.hpp>

#include <algorithm>
#include <random>

#include "test_utils_capture.h"
#include "test_utils_tmpdir.h"
#include "test_utils_ostream.hpp"


auto version_dataset = boost::unit_test::data::make({
      h5features::version::v1_1,
      h5features::version::v2_0});


std::vector<double> generate_vector(std::size_t size)
{
   std::mt19937 engine;
   auto dist = std::uniform_real_distribution<double>{0, 1};

   std::vector<double> vec(size);
   std::generate(vec.begin(), vec.end(), [&](){return dist(engine);});
   return vec;
}


std::vector<double> generate_range(double start, double stop)
{
   std::vector<double> vec(stop - start);
   std::iota(vec.begin(), vec.end(), start);
   return vec;
}


h5features::item generate_item(const std::string& name, std::size_t size, std::size_t dim, bool properties=true)
{
   auto feats = generate_vector(size * dim);
   auto start = generate_range(0, size);
   auto stop = generate_range(0.5, size + 0.5);

   h5features::properties props;
   if(properties)
   {
      props.set<int>("int", 1);
      props.set<std::string>("string", "string");
      props.set<std::vector<double>>("start", start);
   }

   return {name, {feats, dim}, {start, stop}, props};
}


BOOST_DATA_TEST_CASE_F(utils::fixture::temp_directory, test_simple, version_dataset, vers)
{
   const std::string filename = (tmpdir / "test.h5").string();
   {
      // file does not exist
      BOOST_CHECK_THROW(h5features::reader(filename, "group"), h5features::exception);
   }

   {
      // write nothing
      h5features::writer(filename, "group", true, true, vers);
   }

   {
      // read nothing
      h5features::reader reader(filename, "group");
      BOOST_CHECK_EQUAL(reader.filename(), filename);
      BOOST_CHECK_EQUAL(reader.groupname(), "group");
      BOOST_CHECK_EQUAL(reader.items().size(), 0);
      BOOST_CHECK_EQUAL(reader.version(), vers);
   }
}


BOOST_DATA_TEST_CASE_F(utils::fixture::temp_directory, test_rw, version_dataset, vers)
{
   const std::string filename = (tmpdir / "test.h5").string();
   const std::vector<h5features::item> items{
      generate_item("item1", 10, 5),
      generate_item("item2", 7, 5, false)};

   {
      h5features::writer(filename, "group", true, true, vers).write(
         items.begin(), items.end());
   }

   h5features::reader reader(filename, "group");
   BOOST_CHECK_EQUAL(reader.version(), vers);
   BOOST_CHECK_EQUAL(reader.items().size(), 2);
   BOOST_CHECK_EQUAL(reader.items()[0], "item1");
   BOOST_CHECK_EQUAL(reader.items()[1], "item2");

   BOOST_CHECK_EQUAL(reader.read_item("item1"), items[0]);
   BOOST_CHECK_EQUAL(reader.read_item("item2"), items[1]);
   BOOST_CHECK_EQUAL(reader.read_all(), items);

   // TODO partial read!
}
