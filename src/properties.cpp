#include "h5features/properties.h"
#include <memory>
#include <set>
#include <string>

namespace {
struct value_equality_visitor {
  const h5features::properties::value_type &other;

  bool operator()(const std::shared_ptr<h5features::properties> &lhs) const {
    if (auto rhs_ptr = std::get_if<std::shared_ptr<h5features::properties>>(&other)) {
      if (!lhs && !*rhs_ptr)
        return true;
      if (!lhs || !*rhs_ptr)
        return false;
      return *lhs == **rhs_ptr;
    }
    return false;
  }

  template <typename T> bool operator()(const T &lhs) const {
    if (auto rhs_ptr = std::get_if<T>(&other)) {
      return lhs == *rhs_ptr;
    }
    return false;
  }
};

bool compare_variants(const h5features::properties::value_type &lhs, const h5features::properties::value_type &rhs) {
  return std::visit(value_equality_visitor{rhs}, lhs);
}
} // namespace

bool h5features::properties::operator==(const properties &other) const {
  if (this == &other)
    return true;
  if (m_properties.size() != other.m_properties.size())
    return false;
  for (const auto &[key, value] : m_properties) {
    auto it = other.m_properties.find(key);
    if (it == other.m_properties.end())
      return false;
    if (!compare_variants(value, it->second))
      return false;
  }
  return true;
}

bool h5features::properties::operator!=(const properties &other) const { return not(*this == other); }

std::size_t h5features::properties::size() const { return m_properties.size(); }

std::set<std::string> h5features::properties::names() const {
  std::set<std::string> names;
  for (const auto &p : m_properties) {
    names.insert(p.first);
  }
  return names;
}

bool h5features::properties::contains(const std::string &name) const { return m_properties.count(name) == 1; }

void h5features::properties::erase(const std::string &name) { m_properties.erase(name); }
