#ifndef H5FEATURES_V2_WRITER_H
#define H5FEATURES_V2_WRITER_H

#include "h5features/details/writer_interface.h"
#include <optional>

namespace h5features {
namespace v2 {
class writer : public h5features::details::writer_interface {
public:
  writer(hdf5::Group &&group, bool compress, h5features::version version);

  void write(const h5features::item &item) override;

private:
  // The dimension of the features in the group (must be constant according to
  // format specification), fixed on the first item wrote
  std::optional<std::size_t> m_dim_features;

  // The dimension of the times in the group (must be constant according to
  // format specification), fixed on the first item wrote
  std::optional<std::size_t> m_dim_times;

  void check_dim_features(const h5features::item &item);
  void check_dim_times(const h5features::item &item);
};
} // namespace v2
} // namespace h5features

#endif // H5FEATURES_V2_WRITER_H
