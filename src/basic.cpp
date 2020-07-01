#include <h5features.h>
#include <algorithm>
#include <iostream>
#include <random>


std::vector<double> generate_vector(std::size_t size)
{
   std::mt19937 engine;
   auto dist = std::uniform_real_distribution<double>{0, 1};

   std::vector<double> vec(size);
   std::generate(vec.begin(), vec.end(), [&](){return dist(engine);});
   return vec;
}


std::vector<double> generate_range(double start, double stop)
{
   std::vector<double> vec(stop - start);
   std::iota(vec.begin(), vec.end(), start);
   return vec;
}


h5features::item generate_item(const std::string& name, std::size_t size, std::size_t dim, bool properties=true)
{
   auto feats = generate_vector(size * dim);
   auto start = generate_range(0, size);
   auto stop = generate_range(0.5, size + 0.5);

   h5features::properties props;
   if(properties)
   {
      props.set<int>("int", 1);
      props.set<std::string>("string", "string");
      props.set<std::vector<double>>("start", start);
   }

   return {name, {feats, dim}, {start, stop}, props};
}


int main()
{
   const auto item = generate_item("toto", 5, 2, false);

   {
      h5features::writer writer("./test.h5", "features", true, true, h5features::version::v1_1);
      writer.write(item);
   }

   {
      auto item2 = h5features::reader("./test.h5", "features").read_item("toto");
      std::cout << (item2 == item) << std::endl;
   }

   return 0;
}
