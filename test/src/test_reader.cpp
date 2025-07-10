#define BOOST_TEST_MODULE test_reader

#include "test_utils_capture.h"
#include "test_utils_data.h"
#include "test_utils_ostream.h"
#include "test_utils_tmpdir.h"

#include "boost/test/data/test_case.hpp"
#include "boost/test/unit_test.hpp"
#include "h5features/exception.h"
#include "h5features/reader.h"
#include "h5features/version.h"
#include "h5features/writer.h"
#include <iostream>
#include <string>
#include <vector>

auto version_dataset =
    boost::unit_test::data::make({h5features::version::v1_1, h5features::version::v1_2, h5features::version::v2_0});

BOOST_DATA_TEST_CASE_F(utils::fixture::temp_directory, test_simple, version_dataset, vers) {
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
    BOOST_CHECK_EQUAL(h5features::reader::list_groups(filename), std::vector<std::string>{"group"});

    h5features::reader reader(filename, "group");
    BOOST_CHECK_EQUAL(reader.filename(), filename);
    BOOST_CHECK_EQUAL(reader.groupname(), "group");
    BOOST_CHECK_EQUAL(reader.items().size(), 0);
    BOOST_CHECK_EQUAL(reader.version(), vers);
  }
}

BOOST_DATA_TEST_CASE_F(utils::fixture::temp_directory, test_rw, version_dataset, vers) {
  const std::string filename = (tmpdir / "test.h5").string();
  const std::vector<h5features::item> items{utils::generate_item("item1", 10, 5),
                                            utils::generate_item("item2", 7, 5, false)};

  {
    utils::capture_stream captured(std::cerr);
    h5features::writer(filename, "group", true, true, vers).write(items.begin(), items.end());

    if (vers <= h5features::version::v1_1) {
      BOOST_CHECK(captured.contains("ignoring properties while writing item", false));
    }
  }

  const h5features::reader reader(filename, "group");
  BOOST_CHECK_EQUAL(reader.version(), vers);
  BOOST_CHECK_EQUAL(reader.items().size(), 2);
  BOOST_CHECK_EQUAL(reader.items()[0], "item1");
  BOOST_CHECK_EQUAL(reader.items()[1], "item2");

  {
    utils::capture_stream captured(std::cerr);
    BOOST_CHECK_EQUAL(reader.read_item("item2"), items[1]);
    if (vers == h5features::version::v1_1) {
      BOOST_CHECK(captured.contains("ignoring properties while reading"));
    } else {
      BOOST_CHECK(captured.is_empty());
    }
  }

  {
    // read item1 but ignore properties
    const auto item1 = reader.read_item("item1", true);
    BOOST_CHECK_NE(item1, items[0]);
    BOOST_CHECK_EQUAL(item1.times(), items[0].times());
    BOOST_CHECK_EQUAL(item1.features(), items[0].features());
    BOOST_CHECK_EQUAL(false, item1.has_properties());
  }

  {
    // read item1 with properties (properties are ignored in v1.1)
    utils::capture_stream captured(std::cerr);
    const auto item1 = reader.read_item("item1", false);
    if (vers == h5features::version::v1_1) {
      BOOST_CHECK(captured.contains("ignoring properties while reading item"));
      BOOST_CHECK_NE(item1, items[0]);
      BOOST_CHECK_NE(reader.read_all(), items);

      BOOST_CHECK_EQUAL(item1.times(), items[0].times());
      BOOST_CHECK_EQUAL(item1.features(), items[0].features());
      BOOST_CHECK_EQUAL(false, item1.has_properties());
      BOOST_CHECK_NE(item1.properties(), items[0].properties());
    } else {
      BOOST_CHECK(captured.is_empty());
      BOOST_CHECK_EQUAL(item1, items[0]);
      BOOST_CHECK_EQUAL(reader.read_all(), items);
    }
  }
}

BOOST_DATA_TEST_CASE_F(utils::fixture::temp_directory, test_rw_partial, version_dataset, vers) {
  const std::string filename = (tmpdir / "test.h5").string();
  const h5features::item item1{"item1", {{0, 1, 2, 3, 4, 5, 2, 1, 0, 0, 0, 0}, 4}, {{0, 0.2, 0.4}, {0.3, 0.5, 0.7}}};
  const h5features::item item2{"item2", {{0, 1, 2, 3, 4, 5, 2, 1, 1, 1, 1, 1}, 4}, {{0, 0.2, 0.4}, {0.3, 0.5, 0.7}}};
  const h5features::item item3{"item3", {{0, 1, 2, 3, 4, 5, 2, 1, 2, 2, 2, 2}, 4}, {{0, 0.2, 0.4}, {0.3, 0.5, 0.7}}};

  {
    h5features::writer writer(filename, "group", true, true, vers);
    writer.write(item1);
    writer.write(item2);
    writer.write(item3);
  }

  h5features::reader reader(filename, "group");

  {
    const auto item = reader.read_item("item2", -10, 10);
    BOOST_CHECK_EQUAL(item, item2);
  }

  {
    const auto item = reader.read_item("item2", 0, 0.7);
    BOOST_CHECK_EQUAL(item, item2);
    BOOST_CHECK_NO_THROW(item.validate());
  }

  {
    const auto item = reader.read_item("item2", 0, 0.3);
    BOOST_CHECK_NE(item, item1);
    BOOST_CHECK_EQUAL(item.size(), 1);
    BOOST_CHECK_EQUAL(item.times().data(), std::vector<double>({0, 0.3}));
    BOOST_CHECK_EQUAL(item.features().data(), std::vector<double>({0, 1, 2, 3}));
    BOOST_CHECK_NO_THROW(item.validate());
  }

  {
    const auto item = reader.read_item("item2", 0, 0.6);
    BOOST_CHECK_NE(item, item1);
    BOOST_CHECK_EQUAL(item.size(), 2);
    BOOST_CHECK_EQUAL(item.times().data(), std::vector<double>({0, 0.3, 0.2, 0.5}));
    BOOST_CHECK_EQUAL(item.features().data(), std::vector<double>({0, 1, 2, 3, 4, 5, 2, 1}));
    BOOST_CHECK_NO_THROW(item.validate());
  }

  {
    const auto item = reader.read_item("item2", 0.15, 0.6);
    BOOST_CHECK_NE(item, item1);
    BOOST_CHECK_EQUAL(item.size(), 1);
    BOOST_CHECK_EQUAL(item.times().data(), std::vector<double>({0.2, 0.5}));
    BOOST_CHECK_EQUAL(item.features().data(), std::vector<double>({4, 5, 2, 1}));
    BOOST_CHECK_NO_THROW(item.validate());
  }
}
