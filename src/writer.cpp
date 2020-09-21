#include <h5features/writer.h>

#include <h5features/exception.h>
#include <h5features/details/v2_writer.h>
#include <h5features/details/v1_writer.h>


inline std::unique_ptr<h5features::details::writer_interface> get_writer(
   hdf5::Group&& group, bool compress, h5features::version version)
{
   switch(version)
   {
      case h5features::version::v1_1:
      case h5features::version::v1_2:
         return std::make_unique<h5features::v1::writer>(std::move(group), compress, version);
         break;
      case h5features::version::v2_0:
         return std::make_unique<h5features::v2::writer>(std::move(group), compress, version);
         break;
      default:
         throw h5features::exception("unsupported version for writer");
   }
}


std::unique_ptr<h5features::details::writer_interface> init_writer(
   const std::string& filename, const std::string& groupname,
   bool overwrite, bool compress, h5features::version version)
{
   // inhibate HDF5 errors stack printing
   const hdf5::SilenceHDF5 silencer;

   // setup the correct flag for file creation
   auto flag = hdf5::File::Create | hdf5::File::ReadWrite;
   if(overwrite)
   {
      flag = hdf5::File::Overwrite | hdf5::File::ReadWrite;
   }

   try
   {
      // open the file, throw if cannot be opened
      auto file = hdf5::File(filename, flag);

      if(not file.exist(groupname))
      {
         // the group does not exist in the file, create an emtpy one and put the
         // current version in it
         auto group = file.createGroup(groupname);
         h5features::write_version(group, version);
         return get_writer(std::move(group), compress, version);
      }
      else
      {
         auto group = file.getGroup(groupname);

         if(group.getNumberObjects() == 0 and group.getNumberAttributes() == 0)
         {
            // the group already exist but is empty, just put the version attribute in it
            h5features::write_version(group, h5features::current_version);
         }
         else
         {
            // the group already exists in the file and is not empty, ensure the
            // version is supported so we can can write new items in it
            if(h5features::read_version(group) != version)
            {
               throw h5features::exception("non empty group: unsupported h5features version");
            }
         }
         return get_writer(std::move(group), compress, version);
      }
   }
   catch(const hdf5::Exception& e)
   {
      throw h5features::exception(e.what());
   }
}


h5features::writer::writer(
   const std::string& filename, const std::string& group, bool overwrite, bool compress, h5features::version version)
   : m_filename{filename},
     m_groupname{group},
     m_writer{init_writer(filename, group, overwrite, compress, version)}
{}


std::string h5features::writer::filename() const
{
   return m_filename;
}


std::string h5features::writer::groupname() const
{
   return m_groupname;
}


h5features::version h5features::writer::version() const
{
   return m_writer->version();;
}


void h5features::writer::write(const h5features::item& item)
{
   m_writer->write(item);
}
