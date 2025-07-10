#include "h5features/times.h"
#include "h5features/exception.h"
#include <algorithm>
#include <sstream>
#include <utility>
#include <vector>

namespace details {
// Returns a single vector `data` with `start` and `stop` interleaved, such as
// `data[2*i]` is `start[i]` and `data[2*i+1]` is `stop[i]`. Throws
// `h5features::exception` if `start` and `stop` have different sizes.
std::vector<double> init_from_start_stop(const std::vector<double> &start, const std::vector<double> &stop) {
  if (start.size() != stop.size()) {
    throw h5features::exception("tstart and tstop must have the same size");
  }

  std::vector<double> data;
  data.reserve(2 * start.size());
  for (std::size_t i = 0; i < start.size(); ++i) {
    data.push_back(start[i]);
    data.push_back(stop[i]);
  }
  return data;
}

// An iterator used to iterate on interleaved data stored in a vector, i.e. to
// iterate the vector with a step of 2. It is assumed the vector has an even
// size. It is used to efficiently use STL algorithms on interleaved data.
class iterator {
public:
  using iterator_category = std::vector<double>::iterator::iterator_category;
  using value_type = double;
  using difference_type = std::vector<double>::iterator::difference_type;
  using pointer = double *;
  using reference = double &;

  static inline iterator begin_start(const std::vector<double> &v) { return {v.begin()}; }

  static inline iterator end_start(const std::vector<double> &v) { return {v.end()}; }

  static inline iterator begin_stop(const std::vector<double> &v) { return {v.begin() + 1}; }

  static inline iterator end_stop(const std::vector<double> &v) { return {v.end() + 1}; }

  iterator(std::vector<double>::const_iterator it) : m_it{it} {}

  inline bool operator==(const iterator &other) const { return m_it == other.m_it; }

  inline bool operator!=(const iterator &other) const { return m_it != other.m_it; }

  inline iterator &operator++() {
    m_it += 2;
    return *this;
  }

  inline iterator operator++(int) {
    auto result = *this;
    ++(*this);
    return result;
  }

  inline iterator operator+=(int i) {
    m_it += i * 2;
    return *this;
  }

  inline iterator &operator--() {
    m_it -= 2;
    return *this;
  }

  inline iterator operator--(int) {
    auto result = *this;
    --(*this);
    return result;
  }

  inline difference_type operator-(iterator other) const { return (m_it - other.m_it) / 2; }

  inline value_type operator*() const { return *m_it; }

private:
  std::vector<double>::const_iterator m_it;
};
} // namespace details

h5features::times::format h5features::times::get_format(const std::size_t &dim) {
  switch (dim) {
  case 1:
    return format::simple;
    break;
  case 2:
    return format::interval;
    break;
  default:
    throw h5features::exception("invalid times dimension");
  }
}

h5features::times::times(const std::vector<double> &data, format times_format, bool validate)
    : m_data{data}, m_format{times_format} {
  if (validate) {
    this->validate();
  }
}

h5features::times::times(std::vector<double> &&data, format times_format, bool validate)
    : m_data{std::move(data)}, m_format{times_format} {
  if (validate) {
    this->validate();
  }
}

h5features::times::times(const std::vector<double> &start, const std::vector<double> &stop, bool validate)
    : m_data{details::init_from_start_stop(start, stop)}, m_format{format::interval} {
  if (validate) {
    this->validate();
  }
}

bool h5features::times::operator==(const times &other) const noexcept {
  return this == &other or (m_format == other.m_format and m_data == other.m_data);
}

bool h5features::times::operator!=(const times &other) const noexcept { return not(*this == other); }

std::size_t h5features::times::size() const noexcept {
  switch (m_format) {
  case format::simple:
    return m_data.size();
    break;
  default: // format::interval
    return m_data.size() / 2;
    break;
  }
}

std::size_t h5features::times::dim() const noexcept {
  switch (m_format) {
  case format::simple:
    return 1;
    break;
  default: // format::interval
    return 2;
    break;
  }
}

const std::vector<double> &h5features::times::data() const noexcept { return m_data; }

double h5features::times::start() const {
  if (size() == 0) {
    throw h5features::exception("times is empty");
  }

  return *(m_data.begin());
}

double h5features::times::stop() const {
  if (size() == 0) {
    throw h5features::exception("times is empty");
  }

  return *(m_data.rbegin());
}

void h5features::times::validate() const {
  // must have a non-zero size
  if (m_data.size() == 0) {
    throw h5features::exception("timestamps must be non-empty");
  }

  switch (m_format) {
  case format::simple: {
    if (not std::is_sorted(m_data.begin(), m_data.end())) {
      throw h5features::exception("timestamps must be sorted in increasing order");
    }

    break;
  }
  default: // format::interval
  {
    if (m_data.size() % 2 != 0) {
      throw h5features::exception("timestamps must have an even size (as [start, stop] pairs)");
    }

    if (not(std::is_sorted(details::iterator::begin_start(m_data), details::iterator::end_start(m_data)) and
            std::is_sorted(details::iterator::begin_stop(m_data), details::iterator::end_stop(m_data)))) {
      throw h5features::exception("timestamps must be sorted in increasing order");
    }

    // ensure tstart <= tstop for all frames
    for (auto it = m_data.begin(); it != m_data.end(); it += 2) {
      if (*it > *(it + 1)) {
        throw h5features::exception("tstart must be lower or equal to tstop for all timestamps");
      }
    }

    break;
  }
  }
}

std::pair<std::size_t, std::size_t> h5features::times::get_indices(double start, double stop) const {
  if (start >= stop) {
    throw h5features::exception("start must be lower than stop");
  }
  std::pair<std::size_t, std::size_t> indices;
  switch (m_format) {
  case format::simple: {
    indices = {std::distance(m_data.begin(), std::lower_bound(m_data.begin(), m_data.end(), start)),
               std::distance(m_data.begin(), std::upper_bound(m_data.begin(), m_data.end(), stop))};
    break;
  }
  default: // format::interval
  {
    indices = {std::distance(details::iterator::begin_start(m_data),
                             std::lower_bound(details::iterator::begin_start(m_data),
                                              details::iterator::end_start(m_data), start)),
               std::distance(
                   details::iterator::begin_stop(m_data),
                   std::upper_bound(details::iterator::begin_stop(m_data), details::iterator::end_stop(m_data), stop))};
    break;
  }
  }
  // ensure the indices are valid
  if (indices.first >= indices.second) {
    std::stringstream msg;
    msg << "no valid indices for time interval (" << start << ", " << stop << ")";
    throw h5features::exception(msg.str());
  }
  return indices;
}

h5features::times h5features::times::select(const std::size_t &start, const std::size_t &stop) const {
  if (start >= stop) {
    throw h5features::exception("start index must be lower or equal to stop index");
  }
  if (stop > size()) {
    throw h5features::exception("stop index must be lower or equal to size");
  }

  switch (m_format) {
  case format::simple: {
    return {{m_data.begin() + start, m_data.begin() + stop}, format::simple, false};
    break;
  }
  default: // format::interval
  {
    return {{m_data.begin() + start * 2, m_data.begin() + stop * 2}, format::interval, false};
    break;
  }
  }
}
