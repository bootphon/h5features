#ifndef H5FEATURES_PROPERTIES_H
#define H5FEATURES_PROPERTIES_H

#include <h5features/exception.h>
#include <boost/variant.hpp>
#include <set>
#include <string>
#include <unordered_map>
#include <vector>


namespace h5features
{
/**
   \brief Handles the properties attached to a `h5features::item`

   Properties are a set of `(name, value)` pairs. It can be used to store
   attributes attached to features, such as generation parameters.

   - A `h5features::properties` instance is created empty.
   - A `(name, value)` pair is added to it with `set()` and accessed with
     `get()`.
   - The `name` must be a `std::string`.
   - The `value` type must be one specified by `properties::value_type`.

 */
class properties
{
public:
   /**
      \brief The types a property value can take

      Its value can be a scalar (`bool`, `int`, `double` or `std::string`), a
      vector (of `int`, `double` or `std::string`) or another
      `h5features::properties`.

    */
   using value_type = boost::variant<
       boost::recursive_wrapper<properties>,
       bool, int, double, std::string,
       std::vector<int>, std::vector<double>, std::vector<std::string>>;

   /// Constructor
   properties() = default;

   /// Destructor
   virtual ~properties() = default;

   /// Copy constructor
   properties(const properties&) = default;

   /// Move constructor
   properties(properties&&) = default;

   /// Copy operator
   properties& operator=(const properties&) = default;

   /// Move operator
   properties& operator=(properties&&) = default;

   /// Returns `true` if the two properties are equal
   bool operator==(const properties& other) const;

   /// Returns `true` if the two properties are not equal
   bool operator!=(const properties& other) const;

   /// Returns the number of `(name, value)` pairs stored
   std::size_t size() const;

   /// Returns the names of the stored properties
   std::set<std::string> names() const;

   /// Returns true if a value attached to `name` is stored, false otherwise
   bool contains(const std::string& name) const;

   /// Deletes the given `name` from the properties if present
   void erase(const std::string& name);

   /**
      \brief Adds a new `(name, value)` pair in the properties

      The added `value` must of one of the types specified by `properties::value_type`.

      \param name The name of the property
      \param value The value of the property

      \throw h5features::exception If a property with the specified `name`
      already exist

    */
   template<class T>
   void set(const std::string& name, const T& value)
   {
      // if(contains(name))
      // {
      //    throw h5features::exception("property name already exists");
      // }

      m_properties[name] = value;
   }

   /**
      \brief Returns the value of a property given its `name` and type `T`

      The returned `value` must of one of the types specified by `value_type`.

      \param name The name of the property to read.

      \throw h5features::exception If the property with the specified `name`
      does not exist or if the specified type `T` does not match the property
      value.

    */
   template<class T>
   T get(const std::string& name) const
   {
      if(not contains(name))
      {
         throw h5features::exception("property name does not exist");
      }

      try
      {
         return boost::get<T>(m_properties.at(name));
      }
      catch(const boost::bad_get& err)
      {
         throw h5features::exception("failed to cast property to specified type");
      }
   }

   /// Returns an iterator on the beginning of the stored properties
   auto begin() const
   {
      return m_properties.begin();
   }


   /// Returns an iterator at the end of the stored properties
   auto end() const
   {
      return m_properties.end();
   }

protected:
   // The properties container
   std::unordered_map<std::string, value_type> m_properties;
};
}

#endif  // H5FEATURES_PROPERTIES_H
