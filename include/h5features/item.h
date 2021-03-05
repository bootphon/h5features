#ifndef H5FEATURES_ITEM_H
#define H5FEATURES_ITEM_H

#include <h5features/features.h>
#include <h5features/properties.h>
#include <h5features/times.h>
#include <string>
#include <unordered_map>

namespace h5features
{
/**
   \brief Handles the features of a single item (e.g. a speech signal)

   An item is made of 4 components:
   - Its name,
   - the features (`h5features::features`) consist a suite of vectors of
     constant dimension,
   - the timestamps (`h5features::times`) associates a start and stop time to
     each features vector,
   - optionnal properties (`h5features::properties`) attached to the features,
     e.g. algorithm parameters or other attributes.

     This class interfaces such an item between user code and an *h5features*
     file, supporting read and write operations.

 */
class item
{
public:
   template<class T>
   T pbind_features();

   template<class T>
   T pbind_times();
   
   template < class T>
   T pbind_properties();

   // bool pbind_contains(const std::string& name);
   // void pbind_erase(const std::string& name);
   /// Destructor
   virtual ~item() = default;

   /// Copy constructor
   item(const item&) = default;

   /// Move constructor
   item(item&&) = default;

   /// Copy operator
   item& operator=(const item&) = default;

   /// Move operator
   item& operator=(item&&) = default;

   /// @name Constructors
   /// @{
   /**
      Instanciates an item from a `name`, `features`, `times` and optional `properties`

      \param name The name of the item
      \param features The item's features
      \param times The item's timestamps
      \param properties The item's properties, if specified
      \param check When true, ensures the item is valid

      \throw h5features::exception If `check` is true and the item is not valid

      \see h5features::item::validate

    */
   item(
      const std::string& name,
      const h5features::features& features,
      const h5features::times& times,
      const h5features::properties& properties={},
      bool check=true);

   item(
      const std::string& name,
      h5features::features&& features,
      h5features::times&& times,
      h5features::properties&& properties,
      bool check=true);
   /// @}

   /// Returns the dimension of the features
   std::size_t dim() const;

   /// Returns the number of vectors in the features
   std::size_t size() const noexcept;

   /// Returns the item's name
   std::string name() const noexcept;

   /// Returns true if the item has attached properties, false otherwise
   bool has_properties() const noexcept;

   /// Returns the item's features
   const h5features::features& features() const noexcept;

   /// Returns the item's timestamps
   const h5features::times& times() const noexcept;

   /// Returns the item's properties
   const h5features::properties& properties() const noexcept;

   /// Returns true if the two items are equal
   bool operator==(const item& other) const noexcept;

   /// Returns true if the two items are not equal
   bool operator!=(const item& other) const noexcept;

   /**
      \brief Ensures the item has a valid state

      An item is valid if an only if:
      - It's name is not empty
      - It contains at least one features vector
      - The features and timestamps have the same size

      \param deep When true ensure that the features and timestamps are valid as
      well by calling item.features().validate() and item.times().validate().

      \throw h5features::exception If the item is not valid

      \see h5features::features::validate
      \see h5features::times::validate

   */
   void validate(bool deep=false) const;

private:
   // Default constructor not used
   item() = delete;

   // Item name
   std::string m_name;

   // Item features
   h5features::features m_features;

   // Item timestamps
   h5features::times m_times;

   // Item properties (eventually empty)
   h5features::properties m_properties;
};
}

#endif  // H5FEATURES_ITEM_H
