#define BOOST_TEST_MODULE test_features

#include <h5features/exception.h>
#include <h5features/features.h>
#include <boost/test/included/unit_test.hpp>

#include "test_utils_tmpdir.h"
#include "test_utils_ostream.hpp"


BOOST_AUTO_TEST_CASE(test_validate_0)
{
   BOOST_CHECK_THROW(h5features::features().validate(), h5features::exception);
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


// BOOST_FIXTURE_TEST_CASE(test_read_write, utils::fixture::temp_directory)
// {
//    const h5features::features features{{
//          1, 2, 3, 4,
//          2, 3, 4, 5,
//          0, 1, 2, 3}, 4};
//    BOOST_CHECK_EQUAL(features.dim(), 4);
//    BOOST_CHECK_EQUAL(features.size(), 3);

//    {
//       hdf5::File file((tmpdir / "test.h5").string(), hdf5::File::Create | hdf5::File::ReadWrite);
//       hdf5::Group group = file.createGroup("item");
//       h5features::v2::write_features(features, group, true);
//    }

//    {
//       hdf5::File file((tmpdir / "test.h5").string(), hdf5::File::ReadOnly);
//       hdf5::Group group = file.getGroup("item");
//       auto features2 = h5features::v2::read_features(group);
//       BOOST_CHECK_EQUAL(features, features2);
//    }

//    // partial read
//    {
//       hdf5::File file((tmpdir / "test.h5").string(), hdf5::File::ReadOnly);
//       hdf5::Group group = file.getGroup("item");

//       // out of bounds
//       BOOST_CHECK_THROW(h5features::v2::read_features(group, {0, 0}), h5features::exception);
//       BOOST_CHECK_THROW(h5features::v2::read_features(group, {10, 12}), h5features::exception);
//       BOOST_CHECK_THROW(h5features::v2::read_features(group, {0, 12}), h5features::exception);

//       {
//          std::vector<double> expected{1, 2, 3, 4};
//          BOOST_CHECK_EQUAL(h5features::v2::read_features(group, {0, 1}).data(), expected);
//       }

//       {
//          std::vector<double> expected{1, 2, 3, 4, 2, 3, 4, 5};
//          BOOST_CHECK_EQUAL(h5features::v2::read_features(group, {0, 2}).data(), expected);
//       }

//       {
//          std::vector<double> expected{2, 3, 4, 5};
//          BOOST_CHECK_EQUAL(h5features::v2::read_features(group, {1, 2}).data(), expected);
//       }

//       BOOST_CHECK_EQUAL(h5features::v2::read_features(group, {0, 3}), features);
//    }
// }


// BOOST_FIXTURE_TEST_CASE(test_write_bad, utils::fixture::temp_directory)
// {
//    const h5features::features features{{
//          0, 1, 2, 3, 4, 5,
//          2, 3, 4, 5, 6, 7}, 6};

//    {
//       hdf5::File file((tmpdir / "test.h5").string(), hdf5::File::Create | hdf5::File::ReadWrite);
//       hdf5::Group group = file.createGroup("item");

//       BOOST_CHECK_NO_THROW(h5features::v2::write_features(features, group, true));
//       BOOST_CHECK_THROW(h5features::v2::write_features(features, group, true), h5features::exception);

//       hdf5::Group group2 = file.createGroup("item2");
//       BOOST_CHECK_NO_THROW(h5features::v2::write_features(features, group2, true));
//    }
// }


// BOOST_FIXTURE_TEST_CASE(test_read_bad, utils::fixture::temp_directory)
// {
//    const h5features::features features{{
//       0, 1, 2, 3, 4, 5,
//       2, 3, 4, 5, 6, 7}, 6};

//    {
//       hdf5::File file((tmpdir / "test.h5").string(), hdf5::File::Create | hdf5::File::ReadWrite);
//       file.createGroup("item_bad");
//       file.createGroup("item_bad_2").createGroup("features");
//    }

//    {
//       hdf5::File file((tmpdir / "test.h5").string(), hdf5::File::ReadOnly);
//       BOOST_CHECK_THROW(h5features::v2::read_features(file.getGroup("item_bad")), h5features::exception);
//       BOOST_CHECK_THROW(h5features::v2::read_features(file.getGroup("item_bad_2")), h5features::exception);
//    }
// }
