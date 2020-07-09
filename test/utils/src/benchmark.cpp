#include <h5features.h>
#include <chrono>
#include <random>
#include <sstream>
#include <string>
#include <vector>


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

auto timeit = [](auto&& func, auto&&... params)
{
   const auto start = std::chrono::high_resolution_clock::now();
   std::forward<decltype(func)>(func)(std::forward<decltype(params)>(params)...);
   const auto stop = std::chrono::high_resolution_clock::now();
   return std::chrono::duration_cast<std::chrono::milliseconds>(stop - start);
};


inline std::chrono::milliseconds write_benchmark(
   const std::string& filename,
   bool compress,
   h5features::version version,
   const std::vector<h5features::item>& items)
{
   return timeit([&](auto&&...)
   {
      h5features::writer(filename, "group", true, compress, version).write(items.begin(), items.end());
   }, filename, compress, version, items);
}


inline std::chrono::milliseconds read_all_benchmark(const std::string& filename)
{
   return timeit([&](auto&&...)
   {
      auto items = h5features::reader(filename, "group").read_all();
   }, filename);
}

int main()
{
   const std::size_t nitems = 2000;

   std::vector<h5features::item> items;
   for(std::size_t i = 0; i < nitems; ++i)
   {
      std::stringstream name;
      name << "item" << i+1;
      items.push_back(generate_item(name.str(), 100, 10, false));
   }

   auto write_c_v1 = write_benchmark("test.h5", true, h5features::version::v1_1, items);
   auto readall_c_v1 = read_all_benchmark("test.h5");

   auto write_u_v1 = write_benchmark("test.h5", false, h5features::version::v1_1, items);
   auto readall_u_v1 = read_all_benchmark("test.h5");

   auto write_c_v2 = write_benchmark("test.h5", true, h5features::version::v2_0, items);
   auto readall_c_v2 = read_all_benchmark("test.h5");

   auto write_u_v2 = write_benchmark("test.h5", false, h5features::version::v2_0, items);
   auto readall_u_v2 = read_all_benchmark("test.h5");


   std::cout << "write..." << std::endl;
   std::cout << "v1 c " << write_c_v1.count() << std::endl;
   std::cout << "v2 c " << write_c_v2.count() << std::endl;
   std::cout << "v1 u " << write_u_v1.count() << std::endl;
   std::cout << "v2 u " << write_u_v2.count() << std::endl;

   std::cout << "read all..." << std::endl;
   std::cout << "v1 c " << readall_c_v1.count() << std::endl;
   std::cout << "v2 c " << readall_c_v2.count() << std::endl;
   std::cout << "v1 u " << readall_u_v1.count() << std::endl;
   std::cout << "v2 u " << readall_u_v2.count() << std::endl;

   // TODO read random access
}
