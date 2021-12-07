#include <string>
#include <h5features/details/properties_writer.h>


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
   void operator()(const std::vector<h5features::properties>& value) const
   {
      
      auto dataset = m_group.createGroup(m_name);
      for (size_t i = 0; i < value.size(); ++i)
      {
         auto group = dataset.createGroup(m_name + std::string("__") + std::to_string(i) + std::string("$$"));
         h5features::details::write_properties(value[i], group, m_compress);
      }
      
   }
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
      h5features::details::write_properties(properties, group, m_compress);
   }


private:
   hdf5::Group& m_group;
   const std::string& m_name;
   const bool m_compress;
};


void h5features::details::write_properties(const h5features::properties& props, hdf5::Group& group, bool compress)
{
   // ensure the group is empty
   if(group.getNumberObjects() != 0)
   {
      throw h5features::exception("the group is not empty");
   }

   try
   {
      for(const auto& prop : props)
      {
         boost::apply_visitor(
            properties_writer_visitor(group, prop.first, compress), prop.second);
      }
   }
   catch(const std::exception& e)
   {
      std::stringstream msg;
      msg << "failed to write properties: " << e.what();
      throw h5features::exception(msg.str());
   }
}
