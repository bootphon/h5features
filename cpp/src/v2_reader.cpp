#include <h5features/details/v2_reader.h>
#include <h5features/details/properties_reader.h>


class features_reader
{
public:
   h5features::features read(const hdf5::Group& group) const
   {
      // ensure the dataset "features" exists in the group
      if(not group.exist("features"))
      {
         throw h5features::exception("object 'features' does not exist in the group");
      }
      if(hdf5::ObjectType::Dataset != group.getObjectType("features"))
      {
         throw h5features::exception("object 'features' is not a dataset in the group");
      }

      try
      {
         return concrete_read(group);
      }
      catch(...)
      {
         throw h5features::exception("failed to read 'features' in the group");
      }
   }

protected:
   inline std::size_t dim(const hdf5::DataSet& dataset) const
   {
      std::size_t dim;
      dataset.getAttribute("dim").read(dim);
      return dim;
   }

   virtual h5features::features concrete_read(const hdf5::Group& group) const
   {
      const auto dataset = group.getDataSet("features");

      std::vector<double> data;
      dataset.read(data);

      return {std::move(data), dim(dataset), false};
   }
};


class features_partial_reader : public features_reader
{
public:
   features_partial_reader(const std::pair<std::size_t, std::size_t>& indices)
      : m_indices{indices}
   {
      if(m_indices.first >= m_indices.second)
      {
         throw h5features::exception("partial read failed, invalid indices: start >= stop");
      }
}

private:
   std::pair<std::size_t, std::size_t> m_indices;

   h5features::features concrete_read(const hdf5::Group& group) const override
   {
      const auto dataset = group.getDataSet("features");
      const auto size = dataset.getDimensions()[0];
      const auto dim = this->dim(dataset);

      const auto offset = m_indices.first * dim;
      if(offset >= size)
      {
         throw h5features::exception("partial read failed, invalid indices: start >= size");
      }

      const auto count = (m_indices.second - m_indices.first) * dim;
      if(offset + count > size)
      {
         throw h5features::exception("partial read failed, invalid indices: stop > size");
      }

      std::vector<double> data;
      dataset.select({offset}, {count}).read(data);
      return {std::move(data), dim, false};
   }
};



h5features::times read_times(const hdf5::Group& group)
{
   // ensure the dataset "times" exists in the group
   if(not group.exist("times"))
   {
      throw h5features::exception("object 'times' does not exist in the group");
   }
   if(hdf5::ObjectType::Dataset != group.getObjectType("times"))
   {
      throw h5features::exception("object 'times' is not a dataset in the group");
   }

   // read the "times" dataset as a times instance
   try
   {
      const auto dataset = group.getDataSet("times");

      // read data
      std::vector<double> data;
      dataset.read(data);

      // read format
      const std::unordered_map<std::string, h5features::times::format> format_name{
         {"simple", h5features::times::format::simple},
         {"interval", h5features::times::format::interval}};
      std::string f;
      dataset.getAttribute("format").read(f);
      return {data, format_name.at(f), false};
   }
   catch(...)
   {
      throw h5features::exception("failed to read 'times' in the group");
   }
}


class item_reader
{
public:
   item_reader(bool ignore_properties)
      : m_ignore_properties{ignore_properties}
   {}

   h5features::item read(const hdf5::Group& group, const std::string& name) const
   {
      // ensure the dataset exists in the group
      if(not group.exist(name))
      {
         std::stringstream msg;
         msg << "object '" << name << "' does not exist in the group";
         throw h5features::exception(msg.str());
      }

      if(hdf5::ObjectType::Group != group.getObjectType(name))
      {
         std::stringstream msg;
         msg << "object '" << name << "' is not a group";
         throw h5features::exception(msg.str());
      }

      // read and return the item
      try
      {
         return concrete_read(group.getGroup(name), name);
      }
      catch(const h5features::exception& e)
      {
         std::stringstream msg;
         msg << "item '" << name << "': " << e.what();
         throw h5features::exception(msg.str());
      }
      catch(...)
      {
         std::stringstream msg;
         msg << "failed to read item '" << name << "' in the group";
         throw h5features::exception(msg.str());
      }
   }

protected:
   bool m_ignore_properties;

   h5features::properties read_properties(const hdf5::Group& group) const
   {
      h5features::properties properties;
      if(not m_ignore_properties and group.exist("properties"))
      {
         hdf5::Group properties_group = group.getGroup("properties");
         properties = h5features::details::read_properties(properties_group);
      }
      return properties;
   }

   virtual h5features::item concrete_read(const hdf5::Group& group, const std::string& name) const
   {
      return {
         name,
         features_reader().read(group),
         read_times(group),
         read_properties(group),
         false};
   }
};



class item_partial_reader : public item_reader
{
public:
   item_partial_reader(bool ignore_properties, double start, double stop)
      : item_reader{ignore_properties}, m_start{start}, m_stop{stop}
   {}

private:
   double m_start;
   double m_stop;

   h5features::item concrete_read(const hdf5::Group& group, const std::string& name) const override
   {
      auto times = read_times(group);
      try
      {
         auto indices = times.get_indices(m_start, m_stop);
         return {
            name,
            features_partial_reader(indices).read(group),
            times.select(indices.first, indices.second),
            read_properties(group),
            false};
      }
      catch(const h5features::exception&)
      {
         throw h5features::exception("partial read is empty");
      }
   }
};


h5features::v2::reader::reader(hdf5::Group&& group, h5features::version version)
   : h5features::details::reader_interface{std::move(group), version}
{}


std::vector<std::string> h5features::v2::reader::items() const
{
   return m_group.listObjectNames();
}


h5features::item h5features::v2::reader::read_item(const std::string& name, bool ignore_properties) const
{
   return item_reader(ignore_properties).read(m_group, name);
}


h5features::item h5features::v2::reader::read_item(
   const std::string& name, double start, double stop, bool ignore_properties) const
{
   return item_partial_reader(ignore_properties, start, stop).read(m_group, name);
}
