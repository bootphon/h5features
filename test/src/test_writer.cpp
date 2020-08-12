#define BOOST_TEST_MODULE test_writer

#include <h5features/exception.h>
#include <h5features/version.h>
#include <h5features/writer.h>
#include <boost/test/included/unit_test.hpp>
#include <boost/test/data/test_case.hpp>

#include "test_utils_capture.h"
#include "test_utils_tmpdir.h"
#include "test_utils_ostream.hpp"


auto version_dataset = boost::unit_test::data::make({
      h5features::version::v1_1,
      h5features::version::v2_0});


BOOST_DATA_TEST_CASE_F(utils::fixture::temp_directory, test_simple, version_dataset, vers)
{
   const auto filename = (tmpdir / "test.h5").string();
   const h5features::writer writer(filename, "group", false, true, vers);
   BOOST_CHECK_EQUAL(writer.filename(), filename);
   BOOST_CHECK_EQUAL(writer.groupname(), "group");
   BOOST_CHECK_EQUAL(writer.version(), vers);
}


BOOST_FIXTURE_TEST_CASE(test_bad, utils::fixture::temp_directory)
{
   BOOST_CHECK_THROW(h5features::writer(tmpdir.string(), "group"), h5features::exception);
}


BOOST_DATA_TEST_CASE_F(utils::fixture::temp_directory, test_write, version_dataset, vers)
{
   h5features::properties p;
   p.set<bool>("bool", false);
   p.set<int>("zero", 0);
   p.set<double>("pi", 3.14);
   p.set<std::string>("name", "hello");

   h5features::item item{
      "test",
      {{0, 1, 2, 3, 4, 5, 2, 1, 0, 0, 0, 0}, 4},
      {{0, 0.2, 0.4}, {0.3, 0.5, 0.7}},
      p};

   const auto filename = (tmpdir / "test.h5").string();

   {
      // write to root group (empty)
      utils::capture_stream captured(std::cerr);
      BOOST_CHECK_NO_THROW(h5features::writer(filename, "/", true, true, vers).write(item));
      BOOST_CHECK_EQUAL(h5features::writer(filename, "/", true, true, vers).version(), vers);
   }

   {
      h5features::writer writer(filename, "group", true, true, vers);

      utils::capture_stream captured(std::cerr);
      writer.write(item);

      if(vers != h5features::version::v2_0)
      {
         BOOST_CHECK(
            captured.is_equal("WARNING h5features v1.1: ignoring properties while writing item test\n", false));
      }
   }

   {
      hdf5::File file(filename, hdf5::File::ReadOnly);
      auto group = file.getGroup("group");

      BOOST_CHECK_EQUAL(h5features::read_version(group), vers);
      if(vers == h5features::version::v1_1)
      {
         BOOST_CHECK(group.exist("index"));
         BOOST_CHECK(group.exist("items"));
         BOOST_CHECK(group.exist("labels"));
         BOOST_CHECK(group.exist("features"));
      }
      else
      {
         BOOST_CHECK(group.exist("test"));
         BOOST_CHECK(group.exist("test/features"));
         BOOST_CHECK(group.exist("test/times"));
         BOOST_CHECK(group.exist("test/properties"));
      }
   }

   // write a second item

   {
      h5features::writer writer(filename, "group", false, true, vers);

      h5features::item item2{item};
      BOOST_CHECK_THROW(writer.write(item2), h5features::exception);

      h5features::item item3{"item3", item.features(), item.times()};
      writer.write(item3);
   }

   {
      hdf5::File file(filename, hdf5::File::ReadOnly);
      auto group = file.getGroup("group");

      BOOST_CHECK_EQUAL(h5features::read_version(group), vers);
      if(vers != h5features::version::v1_1)
      {
         BOOST_CHECK(group.exist("item3"));
         BOOST_CHECK(group.exist("item3/features"));
         BOOST_CHECK(group.exist("item3/times"));
         BOOST_CHECK(not group.exist("item3/properties"));
      }
   }

   {
      // write another item with a different features dimension
      h5features::item item2{
         "test2",
         {{0, 1, 2, 3}, 2},
         {{0, 0.2, 0.4, 0.6}, h5features::times::format::interval}};

      h5features::writer writer(filename, "group", false, true, vers);

      // in v1_1 this is not possible
      if(vers == h5features::version::v1_1)
      {
         BOOST_CHECK_THROW(writer.write(item2), h5features::exception);
      }
      else
      {
         BOOST_CHECK_NO_THROW(writer.write(item2));
      }
   }

   {
      // write another item with a different times dimension
      h5features::item item2{
         "test3",
         {{0, 1, 2, 3, 4, 5, 2, 1, 0, 0, 0, 0}, 4},
         {{0, 0.2, 0.4}, h5features::times::format::simple}};

      h5features::writer writer(filename, "group", false, true, vers);

      // in v1_1 this is not possible
      if(vers == h5features::version::v1_1)
      {
         BOOST_CHECK_THROW(writer.write(item2), h5features::exception);
      }
      else
      {
         BOOST_CHECK_NO_THROW(writer.write(item2));
      }
   }
}


BOOST_DATA_TEST_CASE_F(utils::fixture::temp_directory, test_flag, version_dataset, vers)
{
   const h5features::item item{
      "item",
      {{0, 1, 2, 3, 4, 5, 2, 1, 0, 0, 0, 0}, 4},
      {{0, 0.2, 0.4}, {0.3, 0.5, 0.7}}};

   const auto filename = (tmpdir / "test.h5").string();

   // write the item a first time
   {
      h5features::writer(filename, "group", false, false, vers).write(item);
   }

   // write the same item in a 2nd group
   {
      h5features::writer(filename, "group2", false, false, vers).write(item);
   }

   // cannot write twice the same item
   BOOST_CHECK_THROW(h5features::writer(filename, "group", false, false, vers).write(item), h5features::exception);

   // overwrite the file
   {
      h5features::writer writer(filename, "group", true, false, vers);
      BOOST_CHECK(hdf5::File(filename, hdf5::File::ReadOnly).exist("group"));
      BOOST_CHECK(not hdf5::File(filename, hdf5::File::ReadOnly).exist("group2"));

      std::string groupname = "group/item";
      if(vers == h5features::version::v1_1)
      {
         groupname = "group/index";
      }

      BOOST_CHECK(not hdf5::File(filename, hdf5::File::ReadOnly).exist(groupname));
      writer.write(item);
      BOOST_CHECK(hdf5::File(filename, hdf5::File::ReadOnly).exist(groupname));
   }
}


BOOST_DATA_TEST_CASE_F(utils::fixture::temp_directory, test_version, version_dataset, vers)
{
   const h5features::item item{
      "item",
      {{0, 1, 2, 3, 4, 5, 2, 1, 0, 0, 0, 0}, 4},
      {{0, 0.2, 0.4}, {0.3, 0.5, 0.7}}};

   const auto filename = (tmpdir / "test.h5").string();

   // write an item
   {
      h5features::writer(filename, "group", true, true, vers).write(item);

      std::string groupname = "group/item";
      if(vers == h5features::version::v1_1)
      {
         groupname = "group/index";
      }
      BOOST_CHECK(hdf5::File(filename, hdf5::File::ReadOnly).exist(groupname));
   }

   // modify version
   {
      auto group = hdf5::File(filename, hdf5::File::ReadWrite).getGroup("group");
      BOOST_CHECK_EQUAL(vers, h5features::read_version(group));
      group.getAttribute("version").write<std::string>("invalid");
   }

   // supress version
   {
      auto group = hdf5::File(filename, hdf5::File::ReadWrite).getGroup("group");
      BOOST_CHECK_THROW(h5features::read_version(group), h5features::exception);
      group.deleteAttribute("version");
      BOOST_CHECK_EQUAL(h5features::version::v0_1, h5features::read_version(group));
   }

   // cannot write: bad version (0.1 is "version" is absent, which is currently
   // unsupported)
   {
      BOOST_CHECK_THROW(h5features::writer(filename, "group", false, false, vers),
                        h5features::exception);
      BOOST_CHECK_NO_THROW(h5features::writer(filename, "group", true));
   }
}
