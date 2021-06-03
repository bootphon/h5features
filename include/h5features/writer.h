#ifndef H5FEATURES_WRITER_H
#define H5FEATURES_WRITER_H

#include <h5features/item.h>
#include <h5features/version.h>
#include <h5features/details/writer_interface.h>
#include <algorithm>
#include <memory>
#include <string>


namespace h5features
{
/**
   \brief The writer class dumps `h5features::item` instances to a HDF5 file

   A writer is non-copyable and is attached to an HDF5 file and a group within
   this file. Each item will then be written as a sub-group in this group.

 */
class writer
{
public:
   /// Destructor
   virtual ~writer() = default;

   /// Move constructor
   writer(writer&&) = default;

   /**
      \brief Instanciates a writer

      \param filename The HDF5 file to write on
      \param group The group in the file to write on
      \param overwrite If true erase the file content if it is already existing.
      If false it will append new items to the existing group.
      \param compress When true, compress the data
      \param version The version of the file to write. Version 1.0 is **not
      available** to write, only read.

      \throw h5features::exception When `overwrite` is true, if the `group`
      already exists in the file and the version is not supported. Or if the
      requested `version` is not supported.

    */
   writer(const std::string& filename, const std::string& group="features",
          bool overwrite=false, bool compress=true,
          h5features::version version=h5features::current_version);

   /**
      \brief Writes a `h5features::item` to disk

      \param item The item to write

      \throw h5features::exception If the item name is already an existing
      object in the group or if the write operation failed.

    */
   void write(const h5features::item& item);

   /**
      \brief Writes a sequence of `h5features::item` to disk

      \param first The begin iterator on the items to write
      \param last The end iterator on the items to write

      \throw h5features::exception If one item is already an existing
      object in the group or if the write operation failed.

   */
   template<class Iterator>
   void write(Iterator&& first, Iterator&& last)
   {
      std::for_each(first, last, [&](const auto& item){write(item);});
   }

   /// Returns the HDF5 file name
   std::string filename() const;

   /// Returns the HDF5 group name
   std::string groupname() const;

   /// Returns the h5features format version being writen
   h5features::version version() const;

private:
   // Default constructor not used
   writer() = delete;

   // Copy disabled
   writer(const writer&) = delete;

   /// Move operator disabled
   writer& operator=(writer&&) = delete;

   // Copy disabled
   writer& operator=(const writer&) = delete;

   // The name of the file to write on
   const std::string m_filename;

   // The name of the group to write on in the file
   const std::string m_groupname;

   // The concrete writer used depends on the h5features version of the file
   std::unique_ptr<h5features::details::writer_interface> m_writer;
};
}

#endif  // H5FEATURES_WRITER_H
