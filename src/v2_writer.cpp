#include <h5features/details/v2_writer.h>


void write_features(const h5features::features& features, hdf5::Group& group, bool compress)
{
   // ensure the dataset "features" does not exist in the group
   if(group.exist("features"))
   {
      throw h5features::exception("object 'features' already exists in the group");
   }

   // The features can be read partially so chunking is important here. We
   // choose a relatively little chunk of 128. This leads to a chunk size of
   // 128*8 = 1kB per dimension. Note that a frame is never split into several
   // chunks.
   hdf5::DataSetCreateProps props;
   props.add(hdf5::Chunking{features.dim() * std::min<std::size_t>(features.size(), std::pow(2, 7))});
   if(compress)
   {
      props.add(hdf5::Deflate{9});
   }

   //create the features dataset and write to it
   try
   {
      auto dataset = group.createDataSet<double>("features", hdf5::DataSpace::From(features.data()), props);
      dataset.write(features.data());
      dataset.createAttribute("dim", features.dim());
   }
   catch(const hdf5::Exception& e)
   {
      throw h5features::exception(std::string("failed to write features: ") + e.what());
   }
}


void write_times(const h5features::times& times, hdf5::Group& group, bool compress)
{
   // ensure the dataset "times" does not exist in the group
   if(group.exist("times"))
   {
      throw h5features::exception("object 'times' already exists in the group");
   }

   // compression is only implemented for chunked data. The times are always
   // read entirely so chunking is not critical here. We use a maximal chunk of
   // 2**15 leading to a maximal chunk size of 524kB (2**15 * 2 channels * 8
   // bytes) (by default the HDF5 chunk cache is 1MB per dataset).
   hdf5::DataSetCreateProps props;
   if(compress)
   {
      props.add(hdf5::Chunking{std::min<std::size_t>(times.size() * times.dim(), std::pow(2, 15))});
      props.add(hdf5::Deflate{9});
   }

   // create the times dataset and write to it
   try
   {
      // write data
      auto dataset = group.createDataSet<double>("times", hdf5::DataSpace::From(times.data()), props);
      dataset.write(times.data());

      // write format
      static const std::unordered_map<std::size_t, std::string> format_name{
         {1, "simple"},
         {2, "interval"}};
      dataset.createAttribute("format", format_name.at(times.dim()));
   }
   catch(...)
   {
      throw h5features::exception("failed to write times");
   }
}


/**
   Write a property to a given HDF5 group

   Internally the scalar properties (bool, int, double and string) are stored as
   attribute within the HDF5 group. The vector properties are stored as dataset
   (optionnally compressed).

 */
void write_properties(const h5features::properties& props, hdf5::Group& group, bool compress);
class properties_writer_visitor : public boost::static_visitor<void>
{
public:
   properties_writer_visitor(hdf5::Group& group, const std::string& name, bool compress)
      : m_group{group}, m_name{name}, m_compress{compress}
   {}

   // write a scalar
   template<class T>
   void operator()(const T& value) const
   {
      m_group.createAttribute<T>(m_name, value);
   }

   // write a vector
   template<class T>
   void operator()(const std::vector<T>& value) const
   {
      hdf5::DataSetCreateProps props;
      if(m_compress)
      {
         props.add(hdf5::Chunking{value.size()});
         props.add(hdf5::Deflate{9});
      }

      m_group.createDataSet<T>(m_name, hdf5::DataSpace::From(value), props).write(value);
   }

   // write a nested property
   void operator()(const h5features::properties& properties) const
   {
      auto group = m_group.createGroup(m_name);
      write_properties(properties, group, m_compress);
   }


private:
   hdf5::Group& m_group;
   const std::string& m_name;
   const bool m_compress;
};


void write_properties(const h5features::properties& props, hdf5::Group& group, bool compress)
{
   // ensure the dataset "properties" does not exist in the group
   if(group.exist("properties"))
   {
      throw h5features::exception("object 'properties' already exists in the group");
   }

   try
   {
      auto props_group = group.createGroup("properties");
      for(const auto& prop : props)
      {
         boost::apply_visitor(
            properties_writer_visitor(props_group, prop.first, compress), prop.second);
      }
   }
   catch(const std::exception& e)
   {
      std::stringstream msg;
      msg << "failed to write properties: " << e.what();
      throw h5features::exception(msg.str());
   }
}


h5features::v2::writer::writer(hdf5::Group&& group, bool compress, h5features::version version)
   : h5features::details::writer_interface{std::move(group), compress, version}
{}


void h5features::v2::writer::write(const h5features::item& item)
{
   // ensure the item does not exist in the group
   if(m_group.exist(item.name()))
   {
      throw h5features::exception("item already exists in the group");
   }

   // write the item to file
   hdf5::Group item_group = m_group.createGroup(item.name());
   write_times(item.times(), item_group, m_compress);
   write_features(item.features(), item_group, m_compress);
   if(item.properties().size() != 0)
   {
      write_properties(item.properties(), item_group, m_compress);
   }
}
