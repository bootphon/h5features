#include <h5features/details/properties_reader.h>


void read_properties_scalar(h5features::properties& props, const std::string& name, const hdf5::Attribute& attribute)
{
   switch(attribute.getDataType().getClass())
   {
      case hdf5::DataTypeClass::Integer:
      {
         // boolean are stored as 8 bits integers
         if(attribute.getDataType().getSize() == 1)
         {
            bool value;
            attribute.read(value);
            props.set(name, value);
         }
         else
         {
            int value;
            attribute.read(value);
            props.set(name, value);
         }
         break;
      }
      case hdf5::DataTypeClass::Float:
      {
         double value;
         attribute.read(value);
         props.set(name, value);
         break;
      }
      case hdf5::DataTypeClass::String:
      {
         std::string value;
         attribute.read(value);
         props.set(name, value);
         break;
      }
      default:
      {
         throw h5features::exception("failed to read properties");
         break;
      }
   }
}


void read_properties_vector(h5features::properties& props, const std::string& name, const hdf5::DataSet& dataset)
{
   switch(dataset.getDataType().getClass())
   {
      case hdf5::DataTypeClass::Integer:
      {
         std::vector<int> value;
         dataset.read(value);
         props.set(name, value);
         break;
      }
      case hdf5::DataTypeClass::Float:
      {
         std::vector<double> value;
         dataset.read(value);
         props.set(name, value);
         break;
      }
      case hdf5::DataTypeClass::String:
      {
         std::vector<std::string> value;
         dataset.read(value);
         props.set(name, value);
         break;
      }
      default:
      {
         throw h5features::exception("failed to read properties");
         break;
      }
   }
}


h5features::properties h5features::details::read_properties(const hdf5::Group& group)
{
   // ensure the group "properties" exists in the group
   if(not group.exist("properties"))
   {
      throw h5features::exception("object 'properties' does not exist in the group");
   }
   if(hdf5::ObjectType::Group != group.getObjectType("properties"))
   {
      throw h5features::exception("object 'properties' is not a subgroup in the group");
   }

   // fill it with the read properties
   h5features::properties props;

   // the properties group to read
   auto props_group = group.getGroup("properties");

   // read all the attributes (correspond to scalar values (bool, int, double) or strings)
   for(const auto& name : props_group.listAttributeNames())
   {
      read_properties_scalar(props, name, props_group.getAttribute(name));
   }

   for(const auto& name : props_group.listObjectNames())
   {
      switch(props_group.getObjectType(name))
      {
         // read dataset (corresponds to vector of int or double)
         case hdf5::ObjectType::Dataset:
         {
            read_properties_vector(props, name, props_group.getDataSet(name));
            break;
         }
         // recusrsive read of nested properties
         case hdf5::ObjectType::Group:
         {
            props.set(name, read_properties(props_group.getGroup(name)));
            break;
         }
         default:
         {
            throw h5features::exception("failed to read properties");
            break;
         }
      }
   }

   return props;
}
