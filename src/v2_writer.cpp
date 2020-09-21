#include <h5features/details/v2_writer.h>
#include <h5features/details/properties_writer.h>


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


void write_properties(const h5features::properties& properties, hdf5::Group& group, bool compress)
{
   if(properties.size() != 0)
   {
      hdf5::Group properties_group = group.createGroup("properties");
      h5features::details::write_properties(properties, properties_group, compress);
   }
}


h5features::v2::writer::writer(hdf5::Group&& group, bool compress, h5features::version version)
   : h5features::details::writer_interface{std::move(group), compress, version},
     m_dim_features{}, m_dim_times{}
{
   if(m_group.hasAttribute("dim_features"))
   {
      std::size_t dim;
      m_group.getAttribute("dim_features").read(dim);
      m_dim_features.emplace(dim);
   }

   if(m_group.hasAttribute("dim_times"))
   {
      std::size_t dim;
      m_group.getAttribute("dim_times").read(dim);
      m_dim_times.emplace(dim);
   }
}


void h5features::v2::writer::write(const h5features::item& item)
{
   // ensure the item does not exist in the group
   if(m_group.exist(item.name()))
   {
      throw h5features::exception("item already exists in the group");
   }

   // ensure the features and times have consistent dimension in the group
   check_dim_features(item);
   check_dim_times(item);

   // write the item to file
   hdf5::Group item_group = m_group.createGroup(item.name());
   write_times(item.times(), item_group, m_compress);
   write_features(item.features(), item_group, m_compress);
   write_properties(item.properties(), item_group, m_compress);
}


void h5features::v2::writer::check_dim_features(const h5features::item& item)
{
   if(m_dim_features.has_value())
   {
      if(m_dim_features.value() != item.dim())
      {
         std::stringstream msg;
         msg << "dimension of existing features is " << m_dim_features.value()
             << ", cannot write features of dimension " << item.dim();
         throw h5features::exception(msg.str());
      }
   }
   else
   {
      // first item, setup the features dimension and write them as attribute in
      // the group
      m_dim_features.emplace(item.dim());
      m_group.createAttribute("dim_features", item.dim());
   }
}


void h5features::v2::writer::check_dim_times(const h5features::item& item)
{
   if(m_dim_times.has_value())
   {
      if(m_dim_times.value() != item.times().dim())
      {
         std::stringstream msg;
         msg << "dimension of existing times is " << m_dim_times.value()
             << ", cannot write times of dimension " << item.times().dim();
         throw h5features::exception(msg.str());
      }
   }
   else
   {
      // first item, setup the timesdimension and write them as attribute in
      // the group
      m_dim_times.emplace(item.times().dim());
      m_group.createAttribute("dim_times", item.times().dim());
   }
}
