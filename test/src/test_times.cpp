#define BOOST_TEST_MODULE test_times

#include <h5features/exception.h>
#include <h5features/times.h>
#include <boost/test/included/unit_test.hpp>
#include <string>
#include <vector>

#include "test_utils_tmpdir.h"
#include "test_utils_ostream.hpp"


BOOST_AUTO_TEST_CASE(test_validate_1)
{
   BOOST_CHECK_EXCEPTION(
      h5features::times({0, 1}, {1, 0}, true), h5features::exception,
      [&](const auto& e){return std::string(e.what()) == "timestamps must be sorted in increasing order";});
   BOOST_CHECK_THROW(h5features::times({0, 1}, {1, 0}, false).validate(), h5features::exception);
}


BOOST_AUTO_TEST_CASE(test_validate_2)
{
   const auto t1 = h5features::times({0, 2}, {1, 1}, false);
   const auto t2 = h5features::times({0, 1, 2, 1}, h5features::times::format::interval, false);

   BOOST_CHECK_EQUAL(t1, t2);

   BOOST_CHECK_EXCEPTION(
      t1.validate(), h5features::exception,
      [&](const auto& e){
         return std::string(e.what()) == "tstart must be lower or equal to tstop for all timestamps";});

   BOOST_CHECK_EXCEPTION(
      t2.validate(), h5features::exception,
      [&](const auto& e){
         return std::string(e.what()) == "tstart must be lower or equal to tstop for all timestamps";});
}


BOOST_AUTO_TEST_CASE(test_validate_3)
{
   BOOST_CHECK_EXCEPTION(
      h5features::times({2, 0}, {1, 1}, true), h5features::exception,
      [&](const auto& e){
         return std::string(e.what()) == "timestamps must be sorted in increasing order";});

   BOOST_CHECK_EXCEPTION(
      h5features::times({2, 0, 1, 1}, h5features::times::format::interval, true), h5features::exception,
      [&](const auto& e){
         return std::string(e.what()) == "timestamps must be sorted in increasing order";});

   BOOST_CHECK_EXCEPTION(
      h5features::times({2, 0, 1, 1}, h5features::times::format::simple, true), h5features::exception,
      [&](const auto& e){
         return std::string(e.what()) == "timestamps must be sorted in increasing order";});

}


BOOST_AUTO_TEST_CASE(test_validate_4)
{
   BOOST_CHECK_EXCEPTION(
      h5features::times({2, 0}, {1}, true), h5features::exception,
      [&](const auto& e){
         return std::string(e.what()) == "tstart and tstop must have the same size";});
}


BOOST_AUTO_TEST_CASE(test_validate_5)
{
   BOOST_CHECK_EXCEPTION(
      h5features::times({}, {}, true), h5features::exception,
      [&](const auto& e){
         return std::string(e.what()) == "timestamps must be non-empty";});
}


BOOST_AUTO_TEST_CASE(test_ctor)
{
   const h5features::times t1{{0, 1, 2}, {0, 1, 2}};
   BOOST_CHECK_EQUAL(3, t1.size());
   BOOST_CHECK_EQUAL(2, t1.dim());
   {
      auto data = std::vector<double>{0, 0, 1, 1, 2, 2};
      BOOST_CHECK_EQUAL(data, t1.data());

      h5features::times t2{data, h5features::times::format::interval};
      BOOST_CHECK(t1 == t2);

      h5features::times t3{data, h5features::times::format::simple};
      BOOST_CHECK(t1 != t3);
   }

   h5features::times t2{t1};
   BOOST_CHECK(t1 == t2);

   h5features::times t3{std::move(t2)};
   BOOST_CHECK(t1 == t3);
   BOOST_CHECK(t2 != t3);
}


BOOST_AUTO_TEST_CASE(test_assign_operator)
{
   const h5features::times t1{{0, 1, 2, 2, 3, 3}, h5features::times::format::simple};

   auto t2 = t1;
   BOOST_CHECK(t1 == t2);

   auto t3 = std::move(t2);
   BOOST_CHECK(t1 == t3);
   BOOST_CHECK(t2 != t3);
}


BOOST_AUTO_TEST_CASE(test_indices_simple)
{
   const h5features::times t{{0, 2, 4, 6, 8}, h5features::times::format::simple};

   {
      std::pair<std::size_t, std::size_t> expected{0, 5};
      BOOST_CHECK_EQUAL(t.get_indices(t.start(), t.stop()), expected);
      BOOST_CHECK_EQUAL(t.get_indices(-10, 10), expected);
      BOOST_CHECK_EQUAL(t.get_indices(-10, 8), expected);
      BOOST_CHECK_EQUAL(t.get_indices(0, 10), expected);
   }

   {
      std::pair<std::size_t, std::size_t> expected{2, 5};
      BOOST_CHECK_EQUAL(t.get_indices(4, t.stop()), expected);
      BOOST_CHECK_EQUAL(t.get_indices(3, 10), expected);
   }

   {
      std::pair<std::size_t, std::size_t> expected{0, 3};
      BOOST_CHECK_EQUAL(t.get_indices(0, 4), expected);
      BOOST_CHECK_EQUAL(t.get_indices(-5, 5), expected);
   }

   {
      BOOST_CHECK_THROW(t.get_indices(3, 3.5), h5features::exception);
   }
}


BOOST_AUTO_TEST_CASE(test_indices_interval)
{
   const h5features::times t{
      {0, 1, 2, 3, 4, 5},
      {2, 3, 4, 5, 6, 7}};

   {
      std::pair<std::size_t, std::size_t> expected{0, 6};
      BOOST_CHECK_EQUAL(t.get_indices(0, 7), expected);
      BOOST_CHECK_EQUAL(t.get_indices(-10, 10), expected);
      BOOST_CHECK_EQUAL(t.get_indices(-10, 7), expected);
      BOOST_CHECK_EQUAL(t.get_indices(0, 10), expected);
   }

   {
      std::pair<std::size_t, std::size_t> expected{1, 6};
      BOOST_CHECK_EQUAL(t.get_indices(1, 7), expected);
      BOOST_CHECK_EQUAL(t.get_indices(0.5, 7), expected);
   }

   {
      std::pair<std::size_t, std::size_t> expected{2, 5};
      BOOST_CHECK_EQUAL(t.get_indices(2, 6), expected);
      BOOST_CHECK_EQUAL(t.get_indices(1.01, 6.8), expected);
   }

   {
      BOOST_CHECK_THROW(t.get_indices(1.2, 1.5), h5features::exception);
   }
}


BOOST_AUTO_TEST_CASE(test_select_simple)
{
   const h5features::times t({0, 1, 2, 3, 4, 5}, h5features::times::format::simple);

   BOOST_CHECK_EQUAL(t.dim(), 1);
   BOOST_CHECK_EQUAL(t.select(0, 6), t);

   const auto t2 = t.select(2, 4);
   t2.validate();
   BOOST_CHECK_EQUAL(t2.size(), 2);
   BOOST_CHECK_EQUAL(t2.dim(), 1);
   BOOST_CHECK_EQUAL(t2.data()[0], 2);
   BOOST_CHECK_EQUAL(t2.data()[1], 3);
   BOOST_CHECK_EQUAL(t2.stop(), 3);
}


BOOST_AUTO_TEST_CASE(test_select_interval)
{
   const h5features::times t{
      {0, 1, 2, 3, 4, 5},
      {2, 3, 4, 5, 6, 7}};

   BOOST_CHECK_THROW(t.select(7, 5), h5features::exception);
   BOOST_CHECK_THROW(t.select(5, 5), h5features::exception);
   BOOST_CHECK_THROW(t.select(5, 7), h5features::exception);

   {
      const auto t2 = t.select(0, 1);
      t2.validate();
      BOOST_CHECK_EQUAL(t2.size(), 1);
      BOOST_CHECK_EQUAL(t2.dim(), 2);
      BOOST_CHECK_EQUAL(t2.data()[0], 0);
      BOOST_CHECK_EQUAL(t2.data()[1], 2);
   }

   {
      const auto t2 = t.select(2, 6);
      t2.validate();
      BOOST_CHECK_EQUAL(t2.size(), 4);
      BOOST_CHECK_EQUAL(t2.dim(), 2);
      BOOST_CHECK_EQUAL(t2.data()[0], 2);
      BOOST_CHECK_EQUAL(t2.data()[1], 4);
      BOOST_CHECK_EQUAL(t2.stop(), 7);
   }

   {
      const auto t2 = t.select(0, 6);
      t2.validate();
      BOOST_CHECK_EQUAL(t2, t);
   }
}


// BOOST_FIXTURE_TEST_CASE(test_read_write, utils::fixture::temp_directory)
// {
//    const h5features::times times{
//       {0, 1, 2, 3, 4, 5},
//       {2, 3, 4, 5, 6, 7}};

//    {
//       hdf5::File file((tmpdir / "test.h5").string(), hdf5::File::Create | hdf5::File::ReadWrite);
//       hdf5::Group group = file.createGroup("item");
//       h5features::v2::write_times(times, group, true);
//    }

//    {
//       hdf5::File file((tmpdir / "test.h5").string(), hdf5::File::ReadOnly);
//       hdf5::Group group = file.getGroup("item");
//       auto times2 = h5features::v2::read_times(group);
//       BOOST_CHECK_EQUAL(times, times2);
//    }
// }


// BOOST_FIXTURE_TEST_CASE(test_write_bad, utils::fixture::temp_directory)
// {
//    const h5features::times times{
//       {0, 1, 2, 3, 4, 5},
//       {2, 3, 4, 5, 6, 7}};

//    {
//       hdf5::File file((tmpdir / "test.h5").string(), hdf5::File::Create | hdf5::File::ReadWrite);
//       hdf5::Group group = file.createGroup("item");
//       h5features::v2::write_times(times, group, true);
//       BOOST_CHECK_THROW(h5features::v2::write_times(times, group, true), h5features::exception);
//       hdf5::Group group2 = file.createGroup("item2");
//       BOOST_CHECK_NO_THROW(h5features::v2::write_times(times, group2, true));
//    }
// }


// BOOST_FIXTURE_TEST_CASE(test_read_bad, utils::fixture::temp_directory)
// {
//    {
//       hdf5::File file((tmpdir / "test.h5").string(), hdf5::File::Create | hdf5::File::ReadWrite);
//       file.createGroup("item_bad");
//       file.createGroup("item_bad_2").createGroup("times");
//    }

//    {
//       hdf5::File file((tmpdir / "test.h5").string(), hdf5::File::ReadOnly);
//       BOOST_CHECK_THROW(h5features::v2::read_times(file.getGroup("item_bad")), h5features::exception);
//       BOOST_CHECK_THROW(h5features::v2::read_times(file.getGroup("item_bad_2")), h5features::exception);
//    }
// }
