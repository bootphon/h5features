#include <h5features/version.h>

#include <h5features/exception.h>
#include <sstream>
#include <string>
#include <unordered_map>


static const std::unordered_map<h5features::version, std::string> version_map{
   {h5features::version::v1_0, "1.0"},
   {h5features::version::v1_1, "1.1"},
   {h5features::version::v1_2, "1.2"},
   {h5features::version::v2_0, "2.0"}};


h5features::version h5features::read_version(const hdf5::Group& group)
{
   static const std::unordered_map<std::string, h5features::version> map{
      {"1.0", h5features::version::v1_0},
      {"1.1", h5features::version::v1_1},
      {"1.2", h5features::version::v1_2},
      {"2.0", h5features::version::v2_0}};

   if(group.hasAttribute("version"))
   {
      std::string version;
      try
      {
         group.getAttribute("version").read(version);
      }
      catch(const hdf5::AttributeException& e)
      {
         // due to a bug in HighFive, a string attribute wrote from h5py cannot
         // be read in HighFive correctly. If we get here, the version is either
         // 1.0 or 1.1.
         if(group.exist("items"))
         {
            version = "1.1";
         }
         else
         {
            version = "1.0";
         }
      }

      try
      {
         return map.at(version);
      }
      catch(const std::out_of_range& e)
      {
         std::stringstream msg;
         msg << "invalid h5features version '" << version.front() << "'";
         throw h5features::exception(msg.str());
      }
   }
   else
   {
      throw h5features::exception("failed to read h5features version");
   }
}


void h5features::write_version(hdf5::Group& group, h5features::version version)
{
   if(group.hasAttribute("version"))
   {
      group.getAttribute("version").write(version_map.at(version));
   }
   else
   {
      group.createAttribute<std::string>("version", version_map.at(version));
   }
}


std::ostream& h5features::operator<<(std::ostream& os, h5features::version v)
{
   os << version_map.at(v);
   return os;
}
