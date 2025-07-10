#include "h5features/features.h"
#include "h5features/exception.h"
#include <vector>

h5features::features::features(const std::vector<double> &data, std::size_t dim, bool check)
    : m_features{data}, m_dim{dim} {
  if (check) {
    validate();
  }
}

h5features::features::features(std::vector<double> &&data, std::size_t dim, bool check) : m_features{data}, m_dim{dim} {
  if (check) {
    validate();
  }
}

bool h5features::features::operator==(const features &other) const noexcept {
  return this == &other or (m_dim == other.m_dim and m_features == other.m_features);
}

bool h5features::features::operator!=(const features &other) const noexcept { return not(*this == other); }

std::size_t h5features::features::dim() const { return m_dim; }

std::size_t h5features::features::size() const noexcept {
  if (m_dim != 0) {
    return m_features.size() / m_dim;
  } else {
    return m_features.size();
  }
}

void h5features::features::validate() const {
  if (m_dim == 0) { // dimension must be positive
    throw h5features::exception("features dimension must be greater than zero");
  }
  if (m_features.size() == 0) { // features must have a non-zero size
    throw h5features::exception("features must have a non-zero size");
  }
  if (m_features.size() % m_dim != 0) { // all features must have the same dimension
    throw h5features::exception("features size must be a multiple of dim");
  }
}

const std::vector<double> &h5features::features::data() const noexcept { return m_features; }
