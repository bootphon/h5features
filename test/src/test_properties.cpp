#define BOOST_TEST_MODULE test_properties

#include "test_utils_ostream.h"
#include "test_utils_tmpdir.h"

#include "boost/test/unit_test.hpp"
#include "h5features/exception.h"
#include "h5features/hdf5.h"
#include "h5features/properties.h"
#include <set>
#include <string>
#include <utility>
#include <vector>

BOOST_AUTO_TEST_CASE(test_default) {
  h5features::properties p;
  BOOST_CHECK_EQUAL(p.size(), 0);
  BOOST_CHECK_EQUAL(p.names().size(), 0);
  BOOST_CHECK_EQUAL(p.contains("foo"), false);
  BOOST_CHECK_EQUAL(p, h5features::properties{});
}

BOOST_AUTO_TEST_CASE(test_lifecycle) {
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

BOOST_AUTO_TEST_CASE(test_erase) {
  h5features::properties p;
  p.set("one", 1);
  p.set("two", 2.0);
  p.set("stuff", std::vector<std::string>{"abc", "def"});

  // BOOST_CHECK_THROW(p.set("one", 2), h5features::exception);

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

BOOST_AUTO_TEST_CASE(test_get) {
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

BOOST_AUTO_TEST_CASE(test_nested) {
  h5features::properties inner;
  inner.set("one", 1);
  inner.set<std::vector<std::string>>("stuff", {"one", "two"});

  h5features::properties outer;
  outer.set("one", 1);
  outer.set<std::vector<std::string>>("stuff", {"one", "two"});
  outer.set("inner", inner);

  BOOST_CHECK_EQUAL(outer.get<h5features::properties>("inner"), inner);
}
