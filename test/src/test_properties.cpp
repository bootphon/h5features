#define BOOST_TEST_MODULE test_properties

#include <h5features/exception.h>
#include <h5features/hdf5.h>
#include <h5features/properties.h>
#include <boost/test/included/unit_test.hpp>
#include <set>
#include <string>
#include <vector>

#include "test_utils_tmpdir.h"
#include "test_utils_ostream.hpp"


// h5features::properties read_write(const std::string& filename, const h5features::properties& properties)
// {
//    {
//       hdf5::File file(filename,  hdf5::File::ReadWrite | hdf5::File::Overwrite);
//       auto group = file.createGroup("features");
//       h5features::v2::write_properties(properties, group, true);
//    }

//    return h5features::v2::read_properties(hdf5::File(filename, hdf5::File::ReadOnly).getGroup("features"));
// }


BOOST_AUTO_TEST_CASE(test_default)
{
   h5features::properties p;
   BOOST_CHECK_EQUAL(p.size(), 0);
   BOOST_CHECK_EQUAL(p.names().size(), 0);
   BOOST_CHECK_EQUAL(p.contains("foo"), false);
   BOOST_CHECK_EQUAL(p, h5features::properties{});
}


BOOST_AUTO_TEST_CASE(test_lifecycle)
{
   h5features::properties p;
   p.set("one", 1);
   p.set("two", 2.0);
   p.set("stuff", std::vector<std::string>{"abc", "def"});

   {
      auto p2 = p;
      BOOST_CHECK_EQUAL(p, p2);
      auto p3 = std::move(p2);
      BOOST_CHECK_EQUAL(p, p3);
      BOOST_CHECK_NE(p2, p3);
   }

   {
      h5features::properties p2(p);
      BOOST_CHECK_EQUAL(p, p2);
      h5features::properties p3(std::move(p2));
      BOOST_CHECK_EQUAL(p, p3);
      BOOST_CHECK_NE(p2, p3);
   }
}


BOOST_AUTO_TEST_CASE(test_erase)
{
   h5features::properties p;
   p.set("one", 1);
   p.set("two", 2.0);
   p.set("stuff", std::vector<std::string>{"abc", "def"});

   BOOST_CHECK_THROW(p.set("one", 2), h5features::exception);

   {
      BOOST_CHECK(p.contains("one"));
      BOOST_CHECK_EQUAL(p.size(), 3);
      const std::set<std::string> names{"one", "two", "stuff"};
      BOOST_CHECK_EQUAL(p.names(), names);
   }

   {
      p.erase("one");
      p.erase("stupid");
      BOOST_CHECK(not p.contains("one"));
      BOOST_CHECK_EQUAL(p.size(), 2);
      const std::set<std::string> names{"two", "stuff"};
      BOOST_CHECK_EQUAL(p.names(), names);
   }
}


BOOST_AUTO_TEST_CASE(test_get)
{
   std::vector<std::string> stuff{"abc", "def"};
   h5features::properties p;
   p.set("one", 1);
   p.set("stuff", stuff);

   BOOST_CHECK_EQUAL(p.get<int>("one"), 1);
   BOOST_CHECK_THROW(p.get<double>("one"), h5features::exception);
   BOOST_CHECK_THROW(p.get<double>("two"), h5features::exception);

   BOOST_CHECK_EQUAL(p.get<std::vector<std::string>>("stuff"), stuff);
   BOOST_CHECK_THROW(p.get<double>("stuff"), h5features::exception);
   BOOST_CHECK_THROW(p.get<std::vector<double>>("stuff"), h5features::exception);
}


// BOOST_FIXTURE_TEST_CASE(test_rw, utils::fixture::temp_directory)
// {
//    h5features::properties p;
//    p.set("bool", false);
//    p.set("zero", 0);
//    p.set("pi", 3.14);
//    p.set("name", std::string{"hello"});
//    p.set<std::vector<double>>("count", {0, 1, 2.2, 3});

//    auto p2 = read_write((tmpdir / "test.h5").string(), p);
//    BOOST_CHECK_EQUAL(p, p2);
// }


// BOOST_FIXTURE_TEST_CASE(test_rw_nested, utils::fixture::temp_directory)
// {
//    h5features::properties p;
//    p.set("bool", false);
//    p.set("zero", 0);
//    p.set("pi", 3.14);
//    p.set("name", std::string{"hello"});
//    p.set<std::vector<double>>("count", {0, 1, 2.2, 3});

//    h5features::properties p2;
//    p2.set("one", 1);
//    p2.set("properties", p);

//    auto p3 = read_write((tmpdir / "test.h5").string(), p2);
//    BOOST_CHECK_EQUAL(p3, p2);
// }


// BOOST_FIXTURE_TEST_CASE(test_write_bad, utils::fixture::temp_directory)
// {
//    const h5features::properties p;
//    hdf5::File file((tmpdir / "test.h5").string(), hdf5::File::Create | hdf5::File::ReadWrite);
//    hdf5::Group group = file.createGroup("items");
//    group.createGroup("properties");

//    BOOST_CHECK_THROW(h5features::v2::write_properties(p, group, true), h5features::exception);
// }


// BOOST_FIXTURE_TEST_CASE(test_read_bad, utils::fixture::temp_directory)
// {
//    {
//       hdf5::File file((tmpdir / "test.h5").string(), hdf5::File::Create | hdf5::File::ReadWrite);
//       file.createGroup("bad_1");
//       file.createGroup("bad_2").createGroup("properties");
//       float one = 1.0;
//       file.createGroup("bad_3").createDataSet<float>("properties", hdf5::DataSpace::From(one)).write(one);
//    }

//    {
//       hdf5::File file((tmpdir / "test.h5").string(), hdf5::File::ReadOnly);
//       BOOST_CHECK_THROW(h5features::v2::read_properties(file.getGroup("bad_1")), h5features::exception);
//       BOOST_CHECK_EQUAL(h5features::v2::read_properties(file.getGroup("bad_2")).size(), 0);
//       BOOST_CHECK_THROW(h5features::v2::read_properties(file.getGroup("bad_3")), h5features::exception);
//    }
// }
