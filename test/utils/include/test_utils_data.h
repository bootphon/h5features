#ifndef H5FEATURES_TEST_UTILS_DATA_H
#define H5FEATURES_TEST_UTILS_DATA_H


#include <h5features/item.h>
#include <h5features/features.h>
#include <h5features/times.h>
#include <vector>


namespace utils
{
/// Generate a random vector with values in [0, 1]
std::vector<double> generate_vector(
   std::size_t size);

std::vector<double> generate_range(
   double start, double stop);

h5features::features generate_features(
   std::size_t size, std::size_t dim);

h5features::times generate_times(
   std::size_t size, h5features::times::format format=h5features::times::format::interval);

h5features::item generate_item(
   const std::string& name, std::size_t size, std::size_t dim, bool properties=true,
   h5features::times::format format=h5features::times::format::interval);
}

#endif  // H5FEATURES_TEST_UTILS_DATA_H
