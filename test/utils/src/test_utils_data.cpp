#include "test_utils_data.h"

#include <h5features/properties.h>
#include <algorithm>
#include <random>


std::vector<double> utils::generate_vector(
   std::size_t size)
{
   static std::mt19937 engine;
   static auto dist = std::uniform_real_distribution<double>{0, 1};

   std::vector<double> vec(size);
   std::generate(vec.begin(), vec.end(), [&](){return dist(engine);});
   return vec;
}


std::vector<double> utils::generate_range(
   double start, double stop)
{
   std::vector<double> vec(stop - start);
   std::iota(vec.begin(), vec.end(), start);
   return vec;
}


h5features::features utils::generate_features(
   std::size_t size, std::size_t dim)
{
   return {generate_vector(size * dim), dim};
}


h5features::times utils::generate_times(
   std::size_t size, h5features::times::format format)
{
   switch(format)
   {
      case h5features::times::format::simple:
         return {generate_range(0, size), format};
         break;
      default:  // format::interval
         return {generate_range(0, size), generate_range(0.5, size + 0.5)};
   }
}


h5features::item utils::generate_item(
   const std::string& name, std::size_t size, std::size_t dim, bool properties)
{
   h5features::properties props;
   if(properties)
   {
      props.set<int>("int", 1);
      props.set<std::string>("string", "string");
      props.set<std::vector<double>>("vector", generate_vector(10));
   }

   return {
      name,
      generate_features(size, dim),
      generate_times(size, h5features::times::format::interval),
      props};
}
