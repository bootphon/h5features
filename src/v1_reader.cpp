#include <h5features/details/v1_reader.h>
#include <h5features/exception.h>
#include <algorithm>
#include <iostream>
#include <sstream>


h5features::v1::reader::reader(hdf5::Group&& group, h5features::version version)
   : h5features::details::reader_interface{std::move(group), version}
{
   std::string items_dataset_name;
   std::string index_dataset_name;
   switch(m_version)
   {
      case h5features::version::v1_1:
         items_dataset_name = "items";
         index_dataset_name = "index";
         break;
      default:
         std::stringstream msg;
         msg << "unsupported h5features format version " << m_version;
         throw h5features::exception(msg.str());
         break;
   }

   try
   {
      m_group.getDataSet(items_dataset_name).read(m_items);
      m_group.getDataSet(index_dataset_name).read(m_index);
   }
   catch(const hdf5::Exception& e)
   {
      throw h5features::exception(std::string("failed to read features: ") + e.what());
   }
}


std::vector<std::string> h5features::v1::reader::items() const
{
   return m_items;
}


h5features::item h5features::v1::reader::read_item(const std::string& name, bool ignore_properties) const
{
   // ensure the item exists
   const auto item_iterator = std::find(m_items.begin(), m_items.end(), name);
   if(item_iterator == m_items.end())
   {
      throw h5features::exception("the requested item does not exist");
   }

   // warn user if proerties are present
   if(m_group.exist("properties") and not ignore_properties)
   {
      std::cerr << "WARNING h5features v1.1: ignoring properties while reading item " << name << std::endl;
   }

   // retrieve the start and stop indices of the item in the index
   const auto position = get_item_position(item_iterator);

   // read the item
   return {
      name,
      {read_features(position)},
      {read_times(position)},
      {},
      false};
}


h5features::item h5features::v1::reader::read_item(
   const std::string& name, double start, double stop, bool ignore_properties) const
{
   // ensure the item exists
   const auto item_iterator = std::find(m_items.begin(), m_items.end(), name);
   if(item_iterator == m_items.end())
   {
      throw h5features::exception("the requested item does not exist");
   }

   // warn user if proerties are present
   if(m_group.exist("properties") and not ignore_properties)
   {
      std::cerr << "WARNING h5features v1.1: ignoring properties while reading item " << name << std::endl;
   }

   // retrieve the start and stop indices of the item in the index
   const auto position = get_item_position(item_iterator);

   // retrieve the sub-position from times
   const auto times = read_times(position);
   const auto subposition = times.get_indices(start, stop);

   return {
      name,
      read_features({position.first + subposition.first, position.second + subposition.first}),
      times.select(subposition.first, subposition.second),
      {},
      false};
}


std::pair<std::size_t, std::size_t> h5features::v1::reader::get_item_position(
   std::vector<std::string>::const_iterator iterator) const
{
   const auto index = std::distance(m_items.begin(), iterator);
   if(index != 0)
   {
      return {m_index[index - 1] + 1, m_index[index] + 1};
   }
   else
   {
      return {0, m_index[0] + 1};
   }
}


h5features::features h5features::v1::reader::read_features(const std::pair<std::size_t, std::size_t>& position) const
{
   try
   {
      const auto dataset = m_group.getDataSet("features");
      const auto dim = dataset.getDimensions()[1];
      std::vector<double> data(dim * (position.second - position.first));
      dataset.select({position.first, 0}, {position.second - position.first, dim}).read(data.data());
      return {data, dim, false};
   }
   catch(const hdf5::Exception& e)
   {
      throw h5features::exception(std::string("failed to read features: ") + e.what());
   }
}


h5features::times h5features::v1::reader::read_times(const std::pair<std::size_t, std::size_t>& position) const
{
   std::string times_name = "times";
   if(m_version == h5features::version::v1_1)
   {
      times_name = "labels";
   }

   try
   {
      const auto dataset = m_group.getDataSet(times_name);
      const auto dim = dataset.getDimensions()[1];
      const auto size = position.second - position.first;
      std::vector<double> data(dim * size);
      dataset.select({position.first, 0}, {size, dim}).read(data.data());
      return {data, h5features::times::get_format(dim), false};
   }
   catch(const hdf5::Exception& e)
   {
      throw h5features::exception(std::string("failed to read times: ") + e.what());
   }
}
