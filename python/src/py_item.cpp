#include "item.h"
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include <pybind11/embed.h>
#include <unordered_map>
#include <iostream>
#include <boost/variant.hpp>
#include <variant>
#include <typeinfo>



void init_item(pybind11::module& m)
{
   pybind11::class_<pybind::item>(m, "ItemWrapper", pybind11::buffer_protocol())
      .def(pybind11::init([](
         const std::string& name,
         const pybind11::buffer & features,
         const pybind11::buffer & begin,
         const pybind11::buffer & end,
         const pybind11::dict & properties,
         bool check = true){
            // auto start = std::chrono::high_resolution_clock::now();

            // create features object
            pybind11::buffer_info info = features.request();
            double *p = (double*)info.ptr;
            std::size_t size = info.size;
            std::size_t shape= info.shape[1];
            auto array = std::vector<double>(p, p+size);
            auto feats = h5features::features(array, shape, check);

            // create times object
            info = begin.request();
            p = (double*)info.ptr;
            size = info.size;
            auto begs = std::vector<double>(p, p+size);
            info = end.request();
            p = (double*)info.ptr;
            auto ens = std::vector<double>(p, p+size);
            auto tims = h5features::times(begs, ens, check);

            // create properties object
            auto props = pybind11::handle(properties).cast<h5features::properties>();
            auto item = pybind::item(name, feats, tims, props, check);

            // auto finish = std::chrono::high_resolution_clock::now();
            // std::chrono::duration<double> elapsed = finish - start;
            // std::cout << "Elapsed time item: " << elapsed.count() << " s\n";
            return item;
         }))
      .def(
         "__eq__",
         &pybind::item::operator==, pybind11::is_operator(),
         "returns true if the two items instances are equal")
      .def(
         "__ne__",
         &pybind::item::operator!=,
         pybind11::is_operator(),
         "returns true if the two items instances are not equal")
      .def(
         "name",
         &pybind::item::name,
         "returns the name of the item")
      .def(
         "has_properties",
         &pybind::item::has_properties,
         "Returns true if the item has attached properties, false otherwise")
      .def(
         "dim",
         &pybind::item::dim,
         "returns the dimension of a feature vector")
      .def(
         "size",
         &pybind::item::size,
         "returns the number of features vectors")
      .def(
         "features",
         &pybind::item::features)
      .def(
         "times",
         &pybind::item::times)
      .def(
         "properties",
         &pybind::item::properties)
      .def(
         "properties_contains",
         &pybind::item::properties_contains)
      .def(
         "properties_erase",
         &pybind::item::erase_properties)
      .def(
         "properties_set",
         &pybind::item::set_properties)
      ;
}
