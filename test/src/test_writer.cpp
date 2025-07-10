#define BOOST_TEST_MODULE test_writer

#include "test_utils_capture.h"
#include "test_utils_data.h"
#include "test_utils_ostream.h"
#include "test_utils_tmpdir.h"

#include "boost/test/data/test_case.hpp"
#include "boost/test/unit_test.hpp"
#include "h5features/exception.h"
#include "h5features/version.h"
#include "h5features/writer.h"

auto version_dataset =
    boost::unit_test::data::make({h5features::version::v1_1, h5features::version::v1_2, h5features::version::v2_0});

BOOST_FIXTURE_TEST_CASE(test_write_1_0, utils::fixture::temp_directory) { // writing v1.0 is not supported
  const auto filename = (tmpdir / "test.h5").string();
  BOOST_CHECK_THROW(h5features::writer(filename, "group", false, false, h5features::version::v1_0),
                    h5features::exception);
}

BOOST_DATA_TEST_CASE_F(utils::fixture::temp_directory, test_simple, version_dataset, vers) {
  const auto filename = (tmpdir / "test.h5").string();
  const h5features::writer writer(filename, "group", false, true, vers);
  BOOST_CHECK_EQUAL(writer.filename(), filename);
  BOOST_CHECK_EQUAL(writer.groupname(), "group");
  BOOST_CHECK_EQUAL(writer.version(), vers);
}

BOOST_FIXTURE_TEST_CASE(test_bad, utils::fixture::temp_directory) { // trying to open a directory
  BOOST_CHECK_THROW(h5features::writer(tmpdir.string(), "group"), h5features::exception);
}

BOOST_DATA_TEST_CASE_F(utils::fixture::temp_directory, test_write, version_dataset, vers) {
  const auto filename = (tmpdir / "test.h5").string();
  const auto item = utils::generate_item("test", 3, 5, true, h5features::times::format::interval);

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

    if (vers == h5features::version::v1_1) {
      BOOST_CHECK(captured.is_equal("WARNING h5features version 1.1: ignoring properties while writing item test (use "
                                    "version 1.2 or greater to save properties)\n",
                                    false));
    }
  }

  {
    hdf5::File file(filename, hdf5::File::ReadOnly);
    auto group = file.getGroup("group");

    BOOST_CHECK_EQUAL(h5features::read_version(group), vers);
    if (vers < h5features::version::v2_0) {
      BOOST_CHECK(group.exist("index"));
      BOOST_CHECK(group.exist("items"));
      BOOST_CHECK(group.exist("labels"));
      BOOST_CHECK(group.exist("features"));
    } else {
      BOOST_CHECK(group.exist("test"));
      BOOST_CHECK(group.exist("test/features"));
      BOOST_CHECK(group.exist("test/times"));
      BOOST_CHECK(group.exist("test/properties"));
    }
  }

  // write a second item
  {
    h5features::writer writer(filename, "group", false, true, vers);

    // cannot write another item with the same name
    h5features::item item2{item};
    BOOST_CHECK_THROW(writer.write(item2), h5features::exception);

    // a different name is OK
    h5features::item item3{"item3", item.features(), item.times()};
    writer.write(item3);
  }

  {
    hdf5::File file(filename, hdf5::File::ReadOnly);
    auto group = file.getGroup("group");

    BOOST_CHECK_EQUAL(h5features::read_version(group), vers);
    if (vers >= h5features::version::v2_0) {
      BOOST_CHECK(group.exist("item3"));
      BOOST_CHECK(group.exist("item3/features"));
      BOOST_CHECK(group.exist("item3/times"));
      BOOST_CHECK(not group.exist("item3/properties"));
    }
  }
}

BOOST_DATA_TEST_CASE_F(utils::fixture::temp_directory, test_write_bad, version_dataset, vers) {
  const auto filename = (tmpdir / "test.h5").string();
  const auto item = utils::generate_item("test", 3, 5, false, h5features::times::format::interval);

  h5features::writer writer(filename, "group", true, true, vers);
  writer.write(item);

  // try to write another item with a different features dimension... but this
  // is not allowed
  {
    const auto item2 = utils::generate_item("test2", 3, item.dim() + 1, true, h5features::times::format::interval);

    BOOST_CHECK_THROW(writer.write(item2), h5features::exception);

    BOOST_CHECK_THROW(h5features::writer(filename, "group", false, true, vers).write(item2), h5features::exception);
  }

  // try to write another item with a different times dimension... again this
  // is not allowed
  {
    const auto item2 = utils::generate_item("test2", 3, item.dim(), true, h5features::times::format::simple);

    BOOST_CHECK_THROW(writer.write(item2), h5features::exception);

    BOOST_CHECK_THROW(h5features::writer(filename, "group", false, true, vers).write(item2), h5features::exception);
  }
}

BOOST_DATA_TEST_CASE_F(utils::fixture::temp_directory, test_flag, version_dataset, vers) {
  const auto filename = (tmpdir / "test.h5").string();
  const auto item = utils::generate_item("item", 3, 4);

  // write the item a first time
  {
    utils::capture_stream captured(std::cerr);
    h5features::writer(filename, "group", false, false, vers).write(item);
  }

  // write the same item in a 2nd group
  {
    utils::capture_stream captured(std::cerr);
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
    if (vers < h5features::version::v2_0) {
      groupname = "group/index";
    }

    BOOST_CHECK(not hdf5::File(filename, hdf5::File::ReadOnly).exist(groupname));
    utils::capture_stream captured(std::cerr);
    writer.write(item);
    BOOST_CHECK(hdf5::File(filename, hdf5::File::ReadOnly).exist(groupname));
  }
}

BOOST_DATA_TEST_CASE_F(utils::fixture::temp_directory, test_version, version_dataset, vers) {
  const auto filename = (tmpdir / "test.h5").string();
  const auto item = utils::generate_item("item", 3, 4);

  // write an item
  {
    utils::capture_stream captured(std::cerr);
    h5features::writer(filename, "group", true, true, vers).write(item);

    std::string groupname = "group/item";
    if (vers < h5features::version::v2_0) {
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
    BOOST_CHECK_THROW(h5features::read_version(group), h5features::exception);
  }

  // cannot write: no version
  {
    BOOST_CHECK_THROW(h5features::writer(filename, "group", false, false, vers), h5features::exception);
    BOOST_CHECK_NO_THROW(h5features::writer(filename, "group", true));
  }
}
