#define BOOST_TEST_MODULE test_item

#include <h5features/exception.h>
#include <h5features/item.h>
#include <boost/test/included/unit_test.hpp>

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


// BOOST_FIXTURE_TEST_CASE(test_rw, utils::fixture::temp_directory)
// {
//    h5features::properties p;
//    p.set("int", 1);
//    p.set("vector_str", std::vector<std::string>{"a", "b", "c"});
//    const h5features::features f{{0, 1, 2, 2, 0, 0, 2, 0, 2}, 3};
//    const h5features::times t{{0, 1, 2}, {1, 2, 3}};

//    const h5features::item item{"item", f, t, p};
//    BOOST_CHECK_EQUAL(item.features(), f);
//    BOOST_CHECK_EQUAL(item.times(), t);
//    BOOST_CHECK_EQUAL(item.properties(), p);

//    {
//       hdf5::File file((tmpdir / "test.h5").string(), hdf5::File::Create | hdf5::File::ReadWrite);
//       auto group = file.createGroup("group");
//       h5features::v2::write_item(item, group, true);
//    }

//    {
//       hdf5::File file((tmpdir / "test.h5").string(), hdf5::File::ReadOnly);
//       auto item2 = h5features::v2::read_item(file.getGroup("group"), "item", false);
//       BOOST_CHECK_EQUAL(item, item2);
//    }

//    {
//       hdf5::File file((tmpdir / "test.h5").string(), hdf5::File::ReadOnly);
//       auto item2 = h5features::v2::read_item(file.getGroup("group"), "item", true);
//       BOOST_CHECK_NE(item, item2);
//       BOOST_CHECK_EQUAL(item2.features(), f);
//       BOOST_CHECK_EQUAL(item2.times(), t);
//       BOOST_CHECK_EQUAL(item2.has_properties(), false);
//    }

//    {
//       hdf5::File file((tmpdir / "test.h5").string(), hdf5::File::ReadOnly);
//       auto item2 = h5features::v2::read_item(file.getGroup("group"), "item", 0, 3, false);
//       BOOST_CHECK_EQUAL(item, item2);
//    }

//    {
//       hdf5::File file((tmpdir / "test.h5").string(), hdf5::File::ReadOnly);
//       BOOST_CHECK_THROW(
//          h5features::v2::read_item(file.getGroup("group"), "item", 1, 1, false), h5features::exception);
//       BOOST_CHECK_THROW(
//          h5features::v2::read_item(file.getGroup("group"), "item", 1, 1.1, false), h5features::exception);
//    }

//    {
//       hdf5::File file((tmpdir / "test.h5").string(), hdf5::File::ReadOnly);
//       auto item2 = h5features::v2::read_item(file.getGroup("group"), "item", 1, 2.5, false);
//       BOOST_CHECK_EQUAL(item2.size(), 1);
//       BOOST_CHECK_EQUAL(item2.times().start(), 1);
//       BOOST_CHECK_EQUAL(item2.times().stop(), 2);
//       BOOST_CHECK_EQUAL(item2.properties(), item.properties());
//       item2.validate(true);
//    }
// }
