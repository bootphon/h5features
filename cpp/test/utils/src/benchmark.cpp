#include <h5features.h>
#include <algorithm>
#include <chrono>
#include <random>
#include <sstream>
#include <string>
#include <vector>


template<class T>
std::vector<T> generate_vector(std::size_t size)
{
   static std::mt19937 engine;
   static auto dist = std::uniform_real_distribution<T>{0, 1};

   std::vector<T> vec(size);
   std::generate(vec.begin(), vec.end(), [&](){return dist(engine);});
   return vec;
}


std::vector<double> generate_range(double start, double stop)
{
   std::vector<double> vec(stop - start);
   std::iota(vec.begin(), vec.end(), start);
   return vec;
}


template<class T>
std::pair<T, T> generate_sorted_pair(const T& min, const T& max)
{
   auto v = generate_vector<T>(2);
   std::sort(v.begin(), v.end());
   return {v[0] * (max - min) + min , v[1] * (max - min) + min};
}


h5features::item generate_item(const std::string& name, std::size_t size, std::size_t dim, bool properties=true)
{
   auto feats = generate_vector<double>(size * dim);
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


std::chrono::milliseconds write_benchmark(
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


std::chrono::milliseconds read_all_benchmark(const std::string& filename)
{
   return timeit([&](auto&&...)
   {
      auto items = h5features::reader(filename, "group").read_all();
   }, filename);
}


std::chrono::milliseconds read_random_one_benchmark(
   const std::string& filename, const std::string& itemname,
   const std::vector<std::pair<double, double>>& intervals)
{
   return timeit([&](auto&&...)
   {
      auto reader = h5features::reader(filename, "group");
      for(auto&& [start, stop] : intervals)
      {
         auto item = reader.read_item(itemname, start, stop);
      }
   }, filename, itemname, intervals);
}


std::chrono::milliseconds read_random_all_benchmark(
   const std::string& filename,
   const std::vector<std::tuple<std::string, double, double>>& intervals)
{
   return timeit([&](auto&&...)
   {
      auto reader = h5features::reader(filename, "group");
      for(auto&& [name, start, stop] : intervals)
      {
        auto item = reader.read_item(name, start, stop);
      }
   }, filename, intervals);
}


int main()
{
   const std::size_t nitems = 2000;

   std::vector<std::string> item_names;
   for(std::size_t i = 0; i < nitems; ++i)
   {
      std::stringstream name;
      name << "item_" << i+1;
      item_names.push_back(name.str());
   }

   std::vector<h5features::item> items;
   for(std::size_t i = 0; i < nitems; ++i)
   {
      std::stringstream name;
      name << "item" << i+1;
      items.push_back(generate_item(item_names[i], 100, 25, false));
   }

   std::vector<std::pair<double, double>> intervals;
   while(intervals.size() < 10000)
   {
      const auto p = generate_sorted_pair<double>(0, 100.5);
      if(p.second - p.first > 2)
      {
         intervals.push_back(p);
      }
   }

   std::vector<std::tuple<std::string, double, double>> named_intervals;
   while(named_intervals.size() < 10000)
   {
      const auto p = generate_sorted_pair<double>(0, 100.5);
      if(p.second - p.first > 2)
      {
         auto name = item_names[rand() % item_names.size()];
         named_intervals.push_back({name, p.first, p.second});
      }
   }

   auto write_c_v1 = write_benchmark("test.h5", true, h5features::version::v1_1, items);
   auto readall_c_v1 = read_all_benchmark("test.h5");
   auto readrandone_c_v1 = read_random_one_benchmark("test.h5", "item_257", intervals);
   auto readrandall_c_v1 = read_random_all_benchmark("test.h5", named_intervals);

   auto write_u_v1 = write_benchmark("test.h5", false, h5features::version::v1_1, items);
   auto readall_u_v1 = read_all_benchmark("test.h5");
   auto readrandone_u_v1 = read_random_one_benchmark("test.h5", "item_257", intervals);
   auto readrandall_u_v1 = read_random_all_benchmark("test.h5", named_intervals);

   auto write_c_v2 = write_benchmark("test.h5", true, h5features::version::v2_0, items);
   auto readall_c_v2 = read_all_benchmark("test.h5");
   auto readrandone_c_v2 = read_random_one_benchmark("test.h5", "item_257", intervals);
   auto readrandall_c_v2 = read_random_all_benchmark("test.h5", named_intervals);

   auto write_u_v2 = write_benchmark("test.h5", false, h5features::version::v2_0, items);
   auto readall_u_v2 = read_all_benchmark("test.h5");
   auto readrandone_u_v2 = read_random_one_benchmark("test.h5", "item_257", intervals);
   auto readrandall_u_v2 = read_random_all_benchmark("test.h5", named_intervals);


   std::cout << "write ..." << std::endl;
   std::cout << "v1 c " << write_c_v1.count() << std::endl;
   std::cout << "v2 c " << write_c_v2.count() << std::endl;
   std::cout << "v1 u " << write_u_v1.count() << std::endl;
   std::cout << "v2 u " << write_u_v2.count() << std::endl;

   std::cout << "read all ..." << std::endl;
   std::cout << "v1 c " << readall_c_v1.count() << std::endl;
   std::cout << "v2 c " << readall_c_v2.count() << std::endl;
   std::cout << "v1 u " << readall_u_v1.count() << std::endl;
   std::cout << "v2 u " << readall_u_v2.count() << std::endl;

   std::cout << "read random one ..." << std::endl;
   std::cout << "v1 c " << readrandone_c_v1.count() << std::endl;
   std::cout << "v2 c " << readrandone_c_v2.count() << std::endl;
   std::cout << "v1 u " << readrandone_u_v1.count() << std::endl;
   std::cout << "v2 u " << readrandone_u_v2.count() << std::endl;

   std::cout << "read random all ..." << std::endl;
   std::cout << "v1 c " << readrandall_c_v1.count() << std::endl;
   std::cout << "v2 c " << readrandall_c_v2.count() << std::endl;
   std::cout << "v1 u " << readrandall_u_v1.count() << std::endl;
   std::cout << "v2 u " << readrandall_u_v2.count() << std::endl;
}
