#ifndef H5FEATURES_WRAPPER_PROPERTIES_H
#define H5FEATURES_WRAPPER_PROPERTIES_H

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <h5features/properties.h>


class properties_wrapper : public h5features::properties
{
public:
   properties_wrapper() = default;
   properties_wrapper(const pybind11::dict& dict);
   properties_wrapper(const h5features::properties& properties);
   properties_wrapper(h5features::properties&& properties);

   void py_set(const std::string& key, const pybind11::handle& value);

   pybind11::iterator py_iter() const;
   pybind11::object py_get(const std::string& name) const;
   pybind11::iterator py_keys() const;
   pybind11::iterator py_items() const;
   pybind11::list py_values() const;
   pybind11::dict py_todict() const;
};


#endif  // H5FEATURES_WRAPPER_PROPERTIES_H
