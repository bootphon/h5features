
#include <h5features/reader.h>
#include <h5features/exception.h>
#include <h5features/details/v1_reader.h>
#include <h5features/details/v2_reader.h>
#include <sstream>


std::unique_ptr<h5features::details::reader_interface> init_reader(
   const std::string& filename, const std::string& groupname)
{
   // inhibate HDF5 errors stack printing (very verbose and useless to end user)
   const hdf5::SilenceHDF5 silencer;

   try
   {
      auto group = hdf5::File{filename, hdf5::File::ReadOnly}.getGroup(groupname);
      auto version = h5features::read_version(group);

      switch(version)
      {
         case h5features::version::v2_0:
         {
            return std::make_unique<h5features::v2::reader>(std::move(group), version);
            break;
         }
         case h5features::version::v1_2:
         case h5features::version::v1_1:
         case h5features::version::v1_0:
         {
            return std::make_unique<h5features::v1::reader>(std::move(group), version);
            break;
         }
         default:
         {
            std::stringstream msg;
            msg << "unsupported h5features version " << version;
            throw h5features::exception(msg.str());
            break;
         }
      }
   }
   catch(const hdf5::Exception& e)
   {
      throw h5features::exception(e.what());
   }
}


h5features::reader::reader(const std::string& filename, const std::string& group)
   : m_filename{filename},
     m_groupname{group},
     m_reader{init_reader(filename, group)}
{}


std::string h5features::reader::filename() const
{
   return m_filename;
}


std::string h5features::reader::groupname() const
{
   return m_groupname;
}


h5features::version h5features::reader::version() const
{
   return m_reader->version();
}


std::vector<std::string> h5features::reader::items() const
{
   return m_reader->items();
}


std::vector<h5features::item> h5features::reader::read_all(bool ignore_properties) const
{
   std::vector<h5features::item> all_items;
   for(const auto& item : items())
   {
      all_items.push_back(read_item(item, ignore_properties));
   }

   return all_items;
}


h5features::item h5features::reader::read_item(const std::string& name, bool ignore_properties) const
{
   return m_reader->read_item(name, ignore_properties);
}


h5features::item h5features::reader::read_item(
   const std::string& name, double start, double stop, bool ignore_properties) const
{
   return m_reader->read_item(name, start, stop, ignore_properties);
}
