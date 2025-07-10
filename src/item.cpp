#include "h5features/item.h"
#include "h5features/exception.h"
#include <string>
#include <utility>

h5features::item::item(const std::string &name, const h5features::features &features, const h5features::times &times,
                       const h5features::properties &properties, bool check)
    : m_name{name}, m_features{features}, m_times{times}, m_properties{properties} {
  if (check) {
    validate();
  }
}

h5features::item::item(const std::string &name, h5features::features &&features, h5features::times &&times,
                       h5features::properties &&properties, bool check)
    : m_name{name}, m_features{std::move(features)}, m_times{std::move(times)}, m_properties{std::move(properties)} {
  if (check) {
    validate();
  }
}

bool h5features::item::operator==(const item &other) const noexcept {
  if (this == &other) {
    return true;
  } else {
    return m_name == other.m_name and m_features == other.m_features and m_times == other.m_times and
           m_properties == other.m_properties;
  }
}

bool h5features::item::operator!=(const item &other) const noexcept { return not(*this == other); }

std::size_t h5features::item::dim() const { return m_features.dim(); }

std::size_t h5features::item::size() const noexcept { return m_features.size(); }

std::string h5features::item::name() const noexcept { return m_name; }

bool h5features::item::has_properties() const noexcept { return m_properties.size() != 0; }

const h5features::times &h5features::item::times() const noexcept { return m_times; }

const h5features::features &h5features::item::features() const noexcept { return m_features; }

const h5features::properties &h5features::item::properties() const noexcept { return m_properties; }

void h5features::item::validate(bool deep) const {
  if (deep) {
    m_times.validate();
    m_features.validate();
  }

  if (m_times.size() != m_features.size()) {
    throw h5features::exception("times and features must have the same size");
  }

  if (size() == 0) {
    throw h5features::exception("item must not be empty");
  }

  if (m_name.size() == 0) {
    throw h5features::exception("item name must not be empty");
  }
}
