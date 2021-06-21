#ifndef H5FEATURES_WRAPPER_ITEM_H
#define H5FEATURES_WRAPPER_ITEM_H

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include <h5features/item.h>


class item_wrapper: public h5features::item
{
public:
   // inherited from h5features::item

   using h5features::item::item;

   inline std::string name() const noexcept
   {
      return h5features::item::name();
   }

   inline std::size_t dim() const noexcept
   {
      return h5features::item::dim();
   }

   inline std::size_t size() const noexcept
   {
      return h5features::item::size();
   }

   inline bool operator==(const item_wrapper& other) const noexcept
   {
      return h5features::item::operator==(other);
   }

   inline bool operator!=(const item_wrapper& other) const noexcept
   {
      return h5features::item::operator!=(other);
   }

   // Specific methods for the wrapper

   static item_wrapper create(
      const std::string& name,
      const pybind11::array_t<double, pybind11::array::c_style | pybind11::array::forcecast>& features,
      const pybind11::array_t<double, pybind11::array::c_style | pybind11::array::forcecast>& times,
      const pybind11::dict& properties,
      bool check = true);

   // required by the reader
   item_wrapper(h5features::item&& item);

   // returns item's features as numpy array
   pybind11::array_t<double> features() const;

   // returns item's time as numpy array
   pybind11::array_t<double> times() const;

   // returns item's properties as dictionnary
   pybind11::dict properties() const;
};


#endif  // H5FEATURES_WRAPPER_ITEM_H
