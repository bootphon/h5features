#include <h5features/details/v1_writer.h>
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

   // warn if properties because they cannot be wrote
   if(item.has_properties())
   {
      std::cerr << "WARNING h5features v" << m_version << ": ignoring properties while writing item "
                << item.name() << std::endl;
   }

   // finally append the item to existing data
   try
   {
      write_index(item);
      write_name(item);
      write_times(item);
      write_features(item);
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
      init_index();
      std::cout << "done init index" << std::endl;
      init_items();
      std::cout << "done init items" << std::endl;
      init_features(dim_features);
      std::cout << "done init features" << std::endl;
      init_times(dim_times);
      std::cout << "done init times" << std::endl;
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
   m_group.createDataSet<std::size_t>("index", hdf5::DataSpace{size, max_size}, props);
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

   m_group.createDataSet<double>(
      "features",
      hdf5::DataSpace{std::vector<std::size_t>{0, dim}, std::vector<std::size_t>{hdf5::DataSpace::UNLIMITED, dim}},
      props);
}


void h5features::v1::writer::init_times(const std::size_t& dim)
{
   // ensure the dataset "times" does not exist in the group
   if(m_group.exist("times"))
   {
      throw h5features::exception("object 'times' already exists in the group");
   }

   hdf5::DataSetCreateProps props;
   props.add(hdf5::Chunking{m_chunk_size, dim});
   if(m_compress)
   {
      props.add(hdf5::Deflate{9});
   }

   m_group.createDataSet<double>(
      "times", hdf5::DataSpace{std::vector<std::size_t>{0, dim}, std::vector<std::size_t>{hdf5::DataSpace::UNLIMITED, dim}}, props);
}


void h5features::v1::writer::check_appendable(const h5features::item& item) const
{
   // check if name is already present
   if(std::find(m_names.begin(), m_names.end(), item.name()) != m_names.end())
   {
      throw h5features::exception("item already exists");
   }

   // check dimension for times
   if(m_group.getDataSet("times").getDimensions()[0] != item.times().dim())
   {
      throw h5features::exception("times dimension mismatch");
   }

   // check dimension for features
   if(m_group.getDataSet("features").getDimensions()[0] != item.features().dim())
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

   // get the current index
   std::size_t index = 0;
   if(size > 1)
   {
      dataset.select(hdf5::ElementSet{size - 2}).read(index);
   }

   // append the updated index to the dataset
   dataset.select(hdf5::ElementSet{size - 1}).write(index + item.size());
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
   dataset.select({size[0] - item.size(), 0}, {item.size(), item.dim()}).write(item.times().data().data());
}


void h5features::v1::writer::write_features(const h5features::item& item)
{
   // get and resize the times dataset by the item size
   auto dataset = m_group.getDataSet("features");
   const auto size = resize_dataset(dataset, item.size());

   // append the features to the dataset
   dataset.select({size[0] - item.size(), 0}, {item.size(), item.dim()}).write(item.features().data().data());
}
