#ifndef H5FEATURES_V1_WRITER_H
#define H5FEATURES_V1_WRITER_H

#include <h5features/details/writer_interface.h>
#include <string>
#include <vector>

namespace h5features
{
namespace v1
{
class writer : public h5features::details::writer_interface
{
public:
   writer(hdf5::Group&& group, bool compress, h5features::version version);

   void write(const h5features::item& item) override;

private:
   const std::size_t m_chunk_size;
   std::vector<std::string> m_names;

   // resize a `dataset` by `increment` over the first dimension, returns the new size
   std::vector<std::size_t> resize_dataset(hdf5::DataSet& dataset, const std::size_t increment);

   void lazy_init(const std::size_t& dim_features, const std::size_t dim_times);
   void init_index();
   void init_items();
   void init_features(const std::size_t& dim);
   void init_times(const std::size_t& dim);

   void check_appendable(const h5features::item& item) const;
   void write_index(const h5features::item& item);
   void write_name(const h5features::item& item);
   void write_times(const h5features::item& item);
   void write_features(const h5features::item& item);
   void write_properties(const h5features::item& item);
};
}
}

#endif  // H5FEATURES_V1_WRITER_H
