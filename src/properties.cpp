#include <h5features/properties.h>


bool h5features::properties::operator==(const properties& other) const
{
   return this == &other or m_properties == other.m_properties;
}


bool h5features::properties::operator!=(const properties& other) const
{
   return not (*this == other);
}


std::size_t h5features::properties::size() const
{
   return m_properties.size();
}


std::set<std::string> h5features::properties::names() const
{
   std::set<std::string> names;
   for(const auto& p : m_properties)
   {
      names.insert(p.first);
   }
   return names;
}

bool h5features::properties::contains(const std::string& name) const
{
   return m_properties.count(name) == 1;
}


void h5features::properties::erase(const std::string& name)
{
   m_properties.erase(name);
}
