#define BOOST_TEST_MODULE test_writer

#include <h5features/exception.h>
#include <h5features/version.h>
#include <h5features/writer.h>
#include <boost/test/included/unit_test.hpp>

#include "test_utils_tmpdir.h"
#include "test_utils_ostream.hpp"


BOOST_FIXTURE_TEST_CASE(test_simple, utils::fixture::temp_directory)
{
   const auto filename = (tmpdir / "test.h5").string();
   const h5features::writer writer(filename, "group");
   BOOST_CHECK_EQUAL(writer.filename(), filename);
   BOOST_CHECK_EQUAL(writer.groupname(), "group");
   BOOST_CHECK_EQUAL(writer.version(), h5features::current_version);
}


BOOST_FIXTURE_TEST_CASE(test_bad, utils::fixture::temp_directory)
{
   BOOST_CHECK_THROW(h5features::writer(tmpdir.string(), "group"), h5features::exception);
}


BOOST_FIXTURE_TEST_CASE(test_write, utils::fixture::temp_directory)
{
   h5features::properties p;
   p.set("bool", false);
   p.set("zero", 0);
   p.set("pi", 3.14);
   p.set("name", std::string{"hello"});

   h5features::item item{
      "item",
      {{0, 1, 2, 3, 4, 5, 2, 1, 0, 0, 0, 0}, 4},
      {{0, 0.2, 0.4}, {0.3, 0.5, 0.7}},
      p};

   const auto filename = (tmpdir / "test.h5").string();

   {
      // write to root group (empty)
      BOOST_CHECK_NO_THROW(h5features::writer(filename, "/").write(item));
      BOOST_CHECK_EQUAL(h5features::writer(filename, "/").version(), h5features::current_version);
   }

   {
      h5features::writer writer(filename, "group");
      writer.write(item);
   }

   {
      hdf5::File file(filename, hdf5::File::ReadOnly);
      auto group = file.getGroup("group");

      BOOST_CHECK_EQUAL(h5features::read_version(group), h5features::current_version);

      BOOST_CHECK(group.exist("item"));
      BOOST_CHECK(group.exist("item/features"));
      BOOST_CHECK(group.exist("item/times"));
      BOOST_CHECK(group.exist("item/properties"));
   }

   // write a second item

   {
      h5features::writer writer(filename, "group", false);

      h5features::item item2{item};
      BOOST_CHECK_THROW(writer.write(item2), h5features::exception);

      h5features::item item3{"item3", item.features(), item.times()};
      writer.write(item3);
   }

   {
      hdf5::File file(filename, hdf5::File::ReadOnly);
      auto group = file.getGroup("group");

      BOOST_CHECK_EQUAL(h5features::read_version(group), h5features::current_version);
      BOOST_CHECK(group.exist("item3"));
      BOOST_CHECK(group.exist("item3/features"));
      BOOST_CHECK(group.exist("item3/times"));
      BOOST_CHECK(not group.exist("item3/properties"));
   }
}


BOOST_FIXTURE_TEST_CASE(test_flag, utils::fixture::temp_directory)
{
   const h5features::item item{
      "item",
      {{0, 1, 2, 3, 4, 5, 2, 1, 0, 0, 0, 0}, 4},
      {{0, 0.2, 0.4}, {0.3, 0.5, 0.7}}};

   const auto filename = (tmpdir / "test.h5").string();

   // write the item a first time
   {
      h5features::writer(filename, "group", false).write(item);
   }

   // write the same item in a 2nd group
   {
      h5features::writer(filename, "group2", false).write(item);
   }

   // cannot write twice the same item
   BOOST_CHECK_THROW(h5features::writer(filename, "group", false).write(item), h5features::exception);

   // overwrite the file
   {
      h5features::writer writer(filename, "group", true);
      BOOST_CHECK(hdf5::File(filename, hdf5::File::ReadOnly).exist("group"));
      BOOST_CHECK(not hdf5::File(filename, hdf5::File::ReadOnly).exist("group2"));
      BOOST_CHECK(not hdf5::File(filename, hdf5::File::ReadOnly).exist("group/item"));

      writer.write(item);
      BOOST_CHECK(hdf5::File(filename, hdf5::File::ReadOnly).exist("group/item"));
   }
}


BOOST_FIXTURE_TEST_CASE(test_version, utils::fixture::temp_directory)
{
   const h5features::item item{
      "item",
      {{0, 1, 2, 3, 4, 5, 2, 1, 0, 0, 0, 0}, 4},
      {{0, 0.2, 0.4}, {0.3, 0.5, 0.7}}};

   const auto filename = (tmpdir / "test.h5").string();

   // write an item
   {
      h5features::writer(filename, "group").write(item);
      BOOST_CHECK(hdf5::File(filename, hdf5::File::ReadOnly).exist("group/item"));
   }

   // modify version
   {
      auto group = hdf5::File(filename, hdf5::File::ReadWrite).getGroup("group");
      BOOST_CHECK_EQUAL(h5features::current_version, h5features::read_version(group));
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
      BOOST_CHECK_THROW(h5features::writer(filename, "group", false), h5features::exception);
      BOOST_CHECK_NO_THROW(h5features::writer(filename, "group", true));
   }
}
