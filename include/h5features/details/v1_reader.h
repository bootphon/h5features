#ifndef H5FEATURES_V1_READER_H
#define H5FEATURES_V1_READER_H

#include <h5features/hdf5.h>
#include <h5features/item.h>
#include <h5features/version.h>
#include <h5features/details/reader_interface.h>
#include <string>
#include <vector>


namespace h5features
{
namespace v1
{
class reader : public h5features::details::reader_interface
{
public:
   reader(hdf5::Group&& group, h5features::version version);

   std::vector<std::string> items() const override;

   h5features::item read_item(
      const std::string& name, bool ignore_properties) const override;

   h5features::item read_item(
      const std::string& name, double start, double stop, bool ignore_properties) const override;

private:
   // The list of items stored in the file
   std::vector<std::string> m_items;

   // The times and features index
   std::vector<std::size_t> m_index;

   // Retrieve position of an item in the index
   std::pair<std::size_t, std::size_t> get_item_position(const std::string& name) const;

   // Loads features from its index position
   h5features::features read_features(const std::pair<std::size_t, std::size_t>& position) const;

   // Loads times from its index position
   h5features::times read_times(const std::pair<std::size_t, std::size_t>& position) const;

   // Loads properties of an item from its name
   h5features::properties read_properties(const std::string& name, bool ignore_properties) const;
};
}
}

#endif  //  H5FEATURES_V1_READER_H
