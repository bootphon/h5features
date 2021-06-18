#ifndef H5FEATURES_READER_H
#define H5FEATURES_READER_H

#include <h5features/item.h>
#include <h5features/version.h>
#include <h5features/details/reader_interface.h>
#include <memory>
#include <string>
#include <vector>


namespace h5features
{
/**
   \brief The reader class reads `h5features::item` from a HDF5 file

   A reader is non-copyable and is attached to an HDF5 file and a group within
   this file.
 */
class reader
{
public:
   /// Destructor
   virtual ~reader() = default;

   /// Move constructor
   reader(reader&&) = default;

   /**
      \brief Instanciates a reader

      \param filename The HDF5 file to read from
      \param group The group within the file to read items from

      \throw h5features::exception If the file cannot be opened or if the group
      does not exist in the file.

    */
   reader(const std::string& filename, const std::string& group);

   /**
      \brief Returns the list of groups in the specified HDF5 file

      \param name The HDF5 file to list the groups from

      \throw h5features::exception If the file cannot be opened
   */
   static std::vector<std::string> list_groups(const std::string& filename);

   /// Returns the name of the file being read
   std::string filename() const;

   /// Returns the name of the group being read in the file
   std::string groupname() const;

   /// Returns the version of the h5features data in the group
   h5features::version version() const;

   /**
      \brief Returns the name of stored items

      The items can be retrieved with `read_all` or `read_item`
   */
   std::vector<std::string> items() const;

   /**
      \brief Returns all the items stored in the file

      \param ignore_properties When true, do not read the item'sproperties

      \throw h5features::exception If the read operation failed.

   */
   std::vector<h5features::item> read_all(bool ignore_properties=false) const;

   /**
      \brief Reads and returns a `h5features::item` instance

      \param name The name of the item to read
      \param ignore_properties When true, do not read the item'sproperties

      \throw h5features::exception If the `name` group does not exist or if the
      read operation failed.

   */
   h5features::item read_item(const std::string& name, bool ignore_properties=false) const;

   /**
      \brief Partial Read of a `h5features::item`

      The method allows to partially load the content of an item, by
      specifiying the time interval `[start, stop]` to load.

      \param name The name of the item to read
      \param start The start time to read the item from
      \param stop The stop time to read the item from
      \param ignore_properties When true, do not read the item's properties

      \throw h5features::exception If the `name` group does not exist or
      if the read operation failed.

   */
   h5features::item read_item(const std::string& name, double start, double stop, bool ignore_properties=false) const;

private:
   // Default constructor not used
   reader() = delete;

   // Copy disabled
   reader(const reader&) = delete;

   /// Move operator deleted
   reader& operator=(reader&&) = delete;

   // Copy disabled
   reader& operator=(const reader&) = delete;

   // The name of the file being read
   const std::string m_filename;

   // The name of the group being read
   const std::string m_groupname;

   // The concrete reader used depends on the h5features version of the file
   std::unique_ptr<h5features::details::reader_interface> m_reader;
};
}


#endif  // H5FEATURES_READER_H
