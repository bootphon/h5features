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


const std::string program = R"code(#!/usr/bin/env python
import numpy as np
import h5features as h5f

items = ['item1', 'item2', 'item3']
times = [
    np.asarray([[0, 1], [1, 2], [2, 3]]),
    np.asarray([[0, 1], [0.5, 1.5], [1, 2]]),
    np.asarray([[0, 1], [1, 2]])]
features = [
    np.asarray([[0, 1.0, 0], [1, 2, 0.0], [2.0, 3, 0]]),
    np.asarray([[10.1, 10, 10], [5.2, 5, 5], [1.3, 2, 3]]),
    np.asarray([[0, 1.0, 0], [1, 2, 0]])]

items = h5f.Data(items, times, features)
h5f.Writer('test.h5', version='1.1').write(items, 'features')
)code";


template<class T>
std::ostream& operator<<(std::ostream& os, std::vector<T> v)
{
   os << "[";
   for(std::size_t i = 0; i < v.size()-1; ++i)
      os << v[i] << " ";
   os << *(v.rbegin()) << "]";
   return os;
}


void read_v11()
{
   int code = std::system(
      (std::string("python -c \"") + program + std::string("\"")).c_str());
   std::cout << "python exit code: " << code << std::endl;

   h5features::reader reader("test.h5", "features");
   std::cout << "version " << reader.version() << std::endl;
   std::cout << "items: ";
   for(const auto& item : reader.items())
      std::cout << item << " ";
   std::cout << std::endl;

   for(const auto& item : reader.read_all())
   {
      std::cout << item.name() << ": " << item.dim() << ", " << item.size()
                << ", t: " << item.times().data()
                << ", f: " << item.features().data()
                << std::endl;
      item.validate();
   }
}


void write_cpp()
{
   const h5features::item item1{
      "item1",
      {{0, 1, 0, 1, 2, 0, 2, 3, 0}, 3},
      {{0, 1, 1, 2, 2, 3}, h5features::times::format::interval}};

   const h5features::item item2{
      "item2",
      {{10.1, 10, 10, 5.2, 5, 5, 1.3, 2, 3}, 3},
      {{0, 1, 0.5, 1.5, 1, 2}, h5features::times::format::interval}};

   const h5features::item item3{
      "item3",
      {{0, 1, 0, 1, 2, 0}, 3},
      {{0, 1, 1, 2}, h5features::times::format::interval}};

   std::cout << item1.name() << " " << item1.size() << " " << item1.dim() << std::endl;
   std::cout << item2.name() << " " << item2.size() << " " << item2.dim() << std::endl;
   std::cout << item3.name() << " " << item3.size() << " " << item3.dim() << std::endl;

   h5features::writer writer("test.h5", "features", true, true, h5features::version::v1_1);
   writer.write(item1);
   writer.write(item2);
   writer.write(item3);
}


int main()
{
   const h5features::item item1{
      "item1",
      {{0, 1, 0, 1, 2, 0, 2, 3, 0}, 3},
      {{0, 1, 1, 2, 2, 3}, h5features::times::format::interval}};

   const h5features::item item2{
      "item2",
      {{10.1, 10, 10, 5.2, 5, 5, 1.3, 2, 3}, 3},
      {{0, 1, 0.5, 1.5, 1, 2}, h5features::times::format::interval}};

   const h5features::item item3{
      "item3",
      {{0, 1, 0, 1, 2, 0}, 3},
      {{0, 1, 1, 2}, h5features::times::format::interval}};

   std::cout << item1.name() << " " << item1.size() << " " << item1.dim() << std::endl;
   std::cout << item2.name() << " " << item2.size() << " " << item2.dim() << std::endl;
   std::cout << item3.name() << " " << item3.size() << " " << item3.dim() << std::endl;

   {
      h5features::writer writer("./test.h5", "features", true, true, h5features::version::v1_1);
      writer.write(item1);
      writer.write(item2);
      writer.write(item3);
      std::cout << "wrote test.h5" << std::endl;
   }

   {
      auto reader = h5features::reader("./test.h5", "features");
      std::cout << "read test.h5, items are: " << reader.items() << std::endl;

      auto read1 = reader.read_item("item1", 0, 1);
      std::cout << read1.times().data() << std::endl;
      std::cout << read1.features().data() << std::endl;
   }

   return 0;
}
