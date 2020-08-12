#define BOOST_TEST_MODULE test_item

#include <h5features/exception.h>
#include <h5features/item.h>
#include <boost/test/included/unit_test.hpp>

#include "test_utils_data.h"
#include "test_utils_tmpdir.h"
#include "test_utils_ostream.hpp"


BOOST_AUTO_TEST_CASE(test_simple)
{
   const h5features::item item{
      "item",
      {{0, 1, 2, 2, 0, 0}, 3},
      {{0, 0}, {1, 1}}};

   BOOST_CHECK_EQUAL(item.has_properties(), false);
   BOOST_CHECK_EQUAL(item.dim(), 3);
   BOOST_CHECK_EQUAL(item.size(), 2);
   BOOST_CHECK_EQUAL(item.name(), "item");
   BOOST_CHECK_EQUAL(item, item);
}


BOOST_AUTO_TEST_CASE(test_comp)
{
   const auto item1 = utils::generate_item("item1", 20, 7, true);
   const auto item2 = utils::generate_item("item2", 30, 7, false);

   BOOST_CHECK_EQUAL(item1.has_properties(), true);
   BOOST_CHECK_EQUAL(item2.has_properties(), false);

   BOOST_CHECK_EQUAL(item1.dim(), 7);
   BOOST_CHECK_EQUAL(item1.size(), 20);
   BOOST_CHECK_EQUAL(item1.name(), "item1");

   BOOST_CHECK(item1 == item1);
   BOOST_CHECK(item1 != item2);
}


BOOST_AUTO_TEST_CASE(test_validate)
{
   // empty name
   {
      h5features::item bad("", utils::generate_features(3, 2), utils::generate_times(3), {}, false);
      BOOST_CHECK_THROW(bad.validate(), h5features::exception);
   }

   // empty features
   {
      h5features::item bad("bad", {{}, 3, false}, utils::generate_times(3), {}, false);
      BOOST_CHECK_THROW(bad.validate(), h5features::exception);
   }

   // empty times
   {
      h5features::item bad("bad", utils::generate_features(3, 2), {{}, {}, false}, {}, false);
      BOOST_CHECK_THROW(bad.validate(), h5features::exception);
   }

   // incompatible times and features
   {
      h5features::item bad("", utils::generate_features(3, 2), utils::generate_times(7), {}, false);
      BOOST_CHECK_THROW(bad.validate(), h5features::exception);
   }
}
