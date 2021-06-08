#define BOOST_TEST_MODULE test_features

#include <h5features/exception.h>
#include <h5features/features.h>
#include <boost/test/included/unit_test.hpp>

#include "test_utils_tmpdir.h"
#include "test_utils_ostream.hpp"


BOOST_AUTO_TEST_CASE(test_validate_0)
{
   BOOST_CHECK_THROW(h5features::features({}, 2, false).validate(), h5features::exception);
}


BOOST_AUTO_TEST_CASE(test_validate_1)
{
   BOOST_CHECK_EXCEPTION(
      h5features::features({}, 1, true), h5features::exception,
      [&](const auto& e){return std::string(e.what()) == "features must have a non-zero size";});

   BOOST_CHECK_EXCEPTION(
      h5features::features({}, 0, true), h5features::exception,
      [&](const auto& e){return std::string(e.what()) == "features dimension must be greater than zero";});

   h5features::features f{{}, 0, false};
   BOOST_CHECK_THROW(f.validate(), h5features::exception);
}


BOOST_AUTO_TEST_CASE(test_validate_2)
{
   BOOST_CHECK_EXCEPTION(
      h5features::features({1, 2, 1, 2, 3}, 3, true), h5features::exception,
      [&](const auto& e){return std::string(e.what()) == "features size must be a multiple of dim";});
}


BOOST_AUTO_TEST_CASE(test_ctor)
{
   const h5features::features f1{{0, 1, 2, 0, 1, 2}, 3};
   BOOST_CHECK_EQUAL(2, f1.size());
   BOOST_CHECK_EQUAL(3, f1.dim());

   {
      auto data = std::vector<double>{0, 1, 2, 0, 1, 2};
      BOOST_CHECK_EQUAL(data, f1.data());
   }

   h5features::features f2{f1};
   BOOST_CHECK(f1 == f2);

   h5features::features f3{std::move(f2)};
   BOOST_CHECK(f1 == f3);
   BOOST_CHECK(f2 != f3);
}


BOOST_AUTO_TEST_CASE(test_assign_operator)
{
   const h5features::features f1{{0, 1, 2, 0, 1, 2}, 3};

   auto f2 = f1;
   BOOST_CHECK(f1 == f2);

   auto f3 = std::move(f2);
   BOOST_CHECK(f1 == f3);
   BOOST_CHECK(f2 != f3);
}
