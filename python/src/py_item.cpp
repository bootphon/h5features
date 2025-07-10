#include "h5features/item.h"
#include "h5features/properties.h"
#include "nanobind/nanobind.h"
#include "nanobind/ndarray.h"
#include "nanobind/stl/optional.h"
#include "nanobind/stl/string.h"
#include "nanobind/stl/unordered_map.h"
#include "nanobind/stl/variant.h"
#include "nanobind/stl/vector.h"
#include <memory>
#include <string>
#include <vector>

namespace nb = nanobind;
using namespace nb::literals;

nb::dict to_py(const h5features::properties &p);
h5features::properties from_py(const nb::dict &d);
h5features::properties::value_type from_py_value(const nb::handle obj);

nb::dict to_py(const h5features::properties &props) {
  nb::dict d;
  for (const auto &[key, value] : props) {
    d[key.c_str()] = std::visit(
        [](const auto &v) -> nb::object {
          using T = std::decay_t<decltype(v)>;
          if constexpr (std::is_same_v<T, std::shared_ptr<h5features::properties>>) {
            return v ? nb::cast(to_py(*v)) : nb::none();
          } else if constexpr (std::is_same_v<T, std::vector<h5features::properties>>) {
            nb::list lst;
            for (const auto &p : v)
              lst.append(to_py(p));
            return lst;
          } else {
            return nb::cast(v);
          }
        },
        value);
  }
  return d;
}

h5features::properties from_py(const nb::dict &d) {
  h5features::properties props;
  for (const auto item : d) {
    std::string key = nb::cast<std::string>(item.first);
    props.set(key, from_py_value(item.second));
  }
  return props;
}

h5features::properties::value_type from_py_value(const nb::handle obj) {
  if (nb::isinstance<nb::dict>(obj)) {
    return std::make_shared<h5features::properties>(from_py(nb::cast<nb::dict>(obj)));
  }
  if (nb::isinstance<nb::bool_>(obj)) {
    return nb::cast<bool>(obj);
  }
  if (nb::isinstance<nb::int_>(obj)) {
    return nb::cast<int>(obj);
  }
  if (nb::isinstance<nb::float_>(obj)) {
    return nb::cast<double>(obj);
  }
  if (nb::isinstance<nb::str>(obj)) {
    return nb::cast<std::string>(obj);
  }
  if (nb::isinstance<nb::ndarray<int, nb::ndim<1>>>(obj)) {
    auto arr = nb::cast<nb::ndarray<int, nb::ndim<1>>>(obj);
    return std::vector<int>{arr.data(), arr.data() + arr.size()};
  }
  if (nb::isinstance<nb::ndarray<double, nb::ndim<1>>>(obj)) {
    auto arr = nb::cast<nb::ndarray<double, nb::ndim<1>>>(obj);
    return std::vector<double>{arr.data(), arr.data() + arr.size()};
  }
  if (nb::isinstance<nb::list>(obj)) {
    nb::list lst(obj);
    if (lst.size() == 0) {
      return std::vector<int>();
    }
    const auto &first = lst[0];
    if (nb::isinstance<nb::dict>(first)) {
      std::vector<h5features::properties> vp;
      vp.reserve(lst.size());
      for (const auto &el : lst)
        vp.push_back(from_py(nb::cast<nb::dict>(el)));
      return vp;
    }
    if (nb::isinstance<nb::int_>(first)) {
      return nb::cast<std::vector<int>>(obj);
    }
    if (nb::isinstance<nb::float_>(first)) {
      return nb::cast<std::vector<double>>(obj);
    }
    if (nb::isinstance<nb::str>(first)) {
      return nb::cast<std::vector<std::string>>(obj);
    }
  }
  throw nb::value_error("Unsupported Python type for h5features::properties");
}

void init_item(nb::module_ &m) {
  nb::class_<h5features::item>(m, "Item")
      .def(
          "__init__",
          [](h5features::item *t, const std::string &name,
             const nb::ndarray<const double, nb::ndim<2>, nb::c_contig> &features,
             const nb::ndarray<const double, nb::c_contig> &times, std::optional<nb::dict> properties) {
            const auto props = properties ? from_py(*properties) : h5features::properties();
            const h5features::features cfeatures{
                std::vector<double>{features.data(), features.data() + features.size()}, features.shape(1), true};
            if (times.ndim() == 1) {
              const h5features::times ctimes{std::vector<double>{times.data(), times.data() + times.size()},
                                             h5features::times::get_format(1), true};
              return new (t) h5features::item(name, cfeatures, ctimes, props);
            } else if (times.ndim() == 2) {
              const h5features::times ctimes{std::vector<double>{times.data(), times.data() + times.size()},
                                             h5features::times::get_format(times.shape(1)), true};
              return new (t) h5features::item(name, cfeatures, ctimes, props);
            }
            throw nb::type_error("Expected a 1D or 2D ndarray for times.");
          },
          "name"_a, "features"_a, "times"_a, "properties"_a = nb::none(),
          "Handle the features of a single item (e.g. a speech signal).")
      .def("__eq__", &h5features::item::operator==, "other"_a)
      .def("__ne__", &h5features::item::operator!=, "other"_a)
      .def_prop_ro("name", &h5features::item::name, "The name of the item.")
      .def_prop_ro("dim", &h5features::item::dim, "The dimension of the features.")
      .def_prop_ro("size", &h5features::item::size, "The number of vectors in the features.")
      .def_prop_ro(
          "properties", [](const h5features::item &self) { return to_py(self.properties()); }, "The item's properties.")
      .def(
          "features",
          [](const h5features::item &self) {
            const auto &cfeatures = self.features();
            return nb::ndarray<nb::numpy, double, nb::ndim<2>, nb::c_contig>(
                const_cast<double *>(cfeatures.data().data()), {cfeatures.size(), cfeatures.dim()});
          },
          "The item's features.")
      .def(
          "times",
          [](const h5features::item &self) {
            const auto &ctimes = self.times();
            return nb::ndarray<nb::numpy, double, nb::ndim<2>, nb::c_contig>(const_cast<double *>(ctimes.data().data()),
                                                                             {ctimes.size(), ctimes.dim()});
          },
          "The item's timestamps.")
      .def("__repr__", [](const h5features::item &self) {
        return nb::str("Item(name={}, size={}, dim={})").format(self.name(), self.size(), self.dim());
      });
}
