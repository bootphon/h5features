#include <h5features/details/v1_writer.h>
#include <iostream>


h5features::v1::writer::writer(hdf5::Group&& group, bool compress, h5features::version version)
   : h5features::details::writer_interface{std::move(group), compress, version},
     m_chunk_size{static_cast<std::size_t>(std::pow(2, 7))},
     m_names{}
{}


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

   m_group.createDataSet<std::size_t>(
      "index", hdf5::DataSpace{{0}, {hdf5::DataSpace::UNLIMITED}});
}


void h5features::v1::writer::init_items()
{
   // ensure the dataset "index" does not exist in the group
   if(m_group.exist("items"))
   {
      throw h5features::exception("object 'items' already exists in the group");
   }

   m_group.createDataSet<std::string>(
      "items", hdf5::DataSpace{{0}, {hdf5::DataSpace::UNLIMITED}});
}


void h5features::v1::writer::init_features(const std::size_t& dim)
{
   // ensure the dataset "features" does not exist in the group
   if(m_group.exist("features"))
   {
      throw h5features::exception("object 'features' already exists in the group");
   }

   hdf5::DataSetCreateProps props;
   props.add(hdf5::Chunking{dim, m_chunk_size});
   if(m_compress)
   {
      props.add(hdf5::Deflate{9});
   }

   m_group.createDataSet<std::string>(
      "features", hdf5::DataSpace{{dim}, {hdf5::DataSpace::UNLIMITED}}, props);
}


void h5features::v1::writer::init_times(const std::size_t& dim)
{
   // ensure the dataset "times" does not exist in the group
   if(m_group.exist("times"))
   {
      throw h5features::exception("object 'times' already exists in the group");
   }

   hdf5::DataSetCreateProps props;
   props.add(hdf5::Chunking{dim, m_chunk_size});
   if(m_compress)
   {
      props.add(hdf5::Deflate{9});
   }

   m_group.createDataSet<std::string>(
      "times", hdf5::DataSpace{{dim}, {hdf5::DataSpace::UNLIMITED}}, props);
}


void h5features::v1::writer::check_appendable(const h5features::item& item) const
{
   // check if name is already present
   if(m_names.count(item.name()) == 1)
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


void h5features::v1::writer::write_index(const h5features::item& item)
{
   std::size_t nitems;
}


void h5features::v1::writer::write_name(const h5features::item& item)
{

}


void h5features::v1::writer::write_times(const h5features::item& item)
{

}


void h5features::v1::writer::write_features(const h5features::item& item)
{

}
