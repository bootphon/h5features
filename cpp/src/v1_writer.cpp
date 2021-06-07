#include <h5features/details/v1_writer.h>
#include <h5features/details/properties_writer.h>
#include <algorithm>
#include <iostream>


h5features::v1::writer::writer(hdf5::Group&& group, bool compress, h5features::version version)
   : h5features::details::writer_interface{std::move(group), compress, version},
     m_chunk_size{static_cast<std::size_t>(std::pow(2, 7))}
{
   // read the name of items already stored (if any)
   try
   {
      m_group.getDataSet("items").read(m_names);
   }
   catch(const hdf5::Exception&)
   {
      m_names.clear();
   }
}


void h5features::v1::writer::write(const h5features::item& item)
{
   // the group does not exist, initialize empty datasets
   if(m_group.getNumberObjects() == 0)
   {
      lazy_init(item.features().dim(), item.times().dim());
   }
   else
   {
      // ensure the item is compatible with the existing data and can be appended
      try
      {
         check_appendable(item);
      }
      catch(const h5features::exception& e)
      {
         throw h5features::exception(std::string("cannot append item to existing group: ") + e.what());
      }
   }

   // on v1_0 or v1.1 warn if properties because they cannot be wrote
   if(m_version <= h5features::version::v1_1 and item.has_properties())
   {
      std::cerr << "WARNING h5features version " << m_version
                << ": ignoring properties while writing item " << item.name()
                << " (use version 1.2 or greater to save properties)" << std::endl;
   }

   // finally append the item to existing data
   try
   {
      write_index(item);
      write_name(item);
      write_times(item);
      write_features(item);
      write_properties(item);
   }
   catch(const hdf5::Exception& e)
   {
      throw h5features::exception(std::string("failed to write item: ") + e.what());
   }
}


void h5features::v1::writer::lazy_init(const std::size_t& dim_features, const std::size_t dim_times)
{
   try
   {
      // "format" attribute is required by v1.1, despite only "dense" value is
      // supported (a planned "sparse" format has never been implemented)
      m_group.createAttribute<std::string>("format", "dense");

      init_index();
      init_items();
      init_features(dim_features);
      init_times(dim_times);
   }
   catch(const hdf5::Exception& e)
   {
      throw h5features::exception(std::string("failed to intialize group: ") + e.what());
   }
}


void h5features::v1::writer::init_index()
{
   // ensure the dataset "index" does not exist in the group
   if(m_group.exist("index"))
   {
      throw h5features::exception("object 'index' already exists in the group");
   }

   hdf5::DataSetCreateProps props;
   props.add(hdf5::Chunking{10});
   if(m_compress)
   {
      props.add(hdf5::Deflate{9});
   }

   const std::vector<std::size_t> size{0};
   const std::vector<std::size_t> max_size{hdf5::DataSpace::UNLIMITED};
   m_group.createDataSet<long long>("index", hdf5::DataSpace{size, max_size}, props);
}


void h5features::v1::writer::init_items()
{
   // ensure the dataset "index" does not exist in the group
   if(m_group.exist("items"))
   {
      throw h5features::exception("object 'items' already exists in the group");
   }

   hdf5::DataSetCreateProps props;
   props.add(hdf5::Chunking{10});
   if(m_compress)
   {
      props.add(hdf5::Deflate{9});
   }

   const std::vector<std::size_t> size{0};
   const std::vector<std::size_t> max_size{hdf5::DataSpace::UNLIMITED};
   m_group.createDataSet<std::string>("items", hdf5::DataSpace{size, max_size}, props);
}


void h5features::v1::writer::init_features(const std::size_t& dim)
{
   // ensure the dataset "features" does not exist in the group
   if(m_group.exist("features"))
   {
      throw h5features::exception("object 'features' already exists in the group");
   }

   hdf5::DataSetCreateProps props;
   props.add(hdf5::Chunking{m_chunk_size, dim});
   if(m_compress)
   {
      props.add(hdf5::Deflate{9});
   }

   const std::vector<std::size_t> size{0, dim};
   const std::vector<std::size_t> max_size{hdf5::DataSpace::UNLIMITED, dim};
   m_group.createDataSet<double>("features", hdf5::DataSpace{size, max_size}, props);
}


void h5features::v1::writer::init_times(const std::size_t& dim)
{
   // ensure the dataset "labels" does not exist in the group
   if(m_group.exist("labels"))
   {
      throw h5features::exception("object 'labels' already exists in the group");
   }

   hdf5::DataSetCreateProps props;
   props.add(hdf5::Chunking{m_chunk_size, dim});
   if(m_compress)
   {
      props.add(hdf5::Deflate{9});
   }

   const std::vector<std::size_t> size{0, dim};
   const std::vector<std::size_t> max_size{hdf5::DataSpace::UNLIMITED, dim};
   m_group.createDataSet<double>("labels", hdf5::DataSpace{size, max_size}, props);
}


void h5features::v1::writer::check_appendable(const h5features::item& item) const
{
   // check if name is already present
   if(std::find(m_names.begin(), m_names.end(), item.name()) != m_names.end())
   {
      throw h5features::exception("item already exists");
   }

   // check dimension for times
   if(m_group.getDataSet("labels").getDimensions()[1] != item.times().dim())
   {
      throw h5features::exception("times dimension mismatch");
   }

   // check dimension for features
   if(m_group.getDataSet("features").getDimensions()[1] != item.features().dim())
   {
      throw h5features::exception("features dimension mismatch");
   }
}


std::vector<std::size_t> h5features::v1::writer::resize_dataset(hdf5::DataSet& dataset, const std::size_t increment)
{
   auto size = dataset.getDimensions();
   size[0] += increment;
   dataset.resize(size);
   return size;
}


void h5features::v1::writer::write_index(const h5features::item& item)
{
   // the index dataset
   auto dataset = m_group.getDataSet("index");

   // resize the dataset (one more element)
   const auto size = resize_dataset(dataset, 1)[0];

   // get the current index and append it to the dataset
   if(size > 1)
   {
      std::size_t index;
      dataset.select(hdf5::ElementSet{size - 2}).read(index);
      dataset.select(hdf5::ElementSet{size - 1}).write(item.size() + index);
   }
   else
   {
      dataset.select(hdf5::ElementSet{size - 1}).write(item.size() - 1);
   }
}


void h5features::v1::writer::write_name(const h5features::item& item)
{
   m_names.push_back(item.name());

   // the names dataset
   auto dataset = m_group.getDataSet("items");

   // resize the dataset (one more element)
   const auto size = resize_dataset(dataset, 1)[0];

   // append the item name to the dataset
   dataset.select(hdf5::ElementSet{size - 1}).write(item.name());
}


void h5features::v1::writer::write_times(const h5features::item& item)
{
   // get and resize the times dataset by the item size
   auto dataset = m_group.getDataSet("labels");
   const auto size = resize_dataset(dataset, item.size());

   // append the times to the dataset
   dataset.select({size[0] - item.size(), 0}, {item.size(), item.times().dim()}).write_raw(
      item.times().data().data());
}


void h5features::v1::writer::write_features(const h5features::item& item)
{
   // get and resize the times dataset by the item size
   auto dataset = m_group.getDataSet("features");
   const auto size = resize_dataset(dataset, item.size());

   // append the features to the dataset
   dataset.select({size[0] - item.size(), 0}, {item.size(), item.dim()}).write_raw(
      item.features().data().data());
}


void h5features::v1::writer::write_properties(const h5features::item& item)
{
   if (item.has_properties())
   {
      // retrieve the "properties" group, creating it if not existing
      if(not m_group.exist("properties"))
      {
         m_group.createGroup("properties");
      }
      hdf5::Group properties_group = m_group.getGroup("properties");

      // create the properties group for that item
      hdf5::Group item_group = properties_group.createGroup(item.name());

      // write its properties within it
      h5features::details::write_properties(item.properties(), item_group, m_compress);
   }
}
