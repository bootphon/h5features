#include <pbreader.h>

pbreader::pbreader(const std::string& filename,const std::string& group) : reader::reader(filename, group) {}
pybind11::list pbreader::items() 
    {return pybind11::cast(reader::items());}
pybind::item pbreader::read(const std::string& name, bool ignore_properties) 
{
    
    // std::unique_ptr<pbitem> it =  std::unique_ptr<pbitem>(dynamic_cast<pbitem*>(std::make_unique<h5features::item>(reader::read_item(name, ignore_properties=ignore_properties)).get())); 
    return pybind::item(reader::read_item(name, ignore_properties=ignore_properties));
}
pybind::item pbreader::read_btw(const std::string& name, double start, double stop, bool ignore_properties)
{
    // std::unique_ptr<pbitem> it =  std::unique_ptr<pbitem>(dynamic_cast<pbitem*>(std::make_unique<h5features::item>(reader::read_item(name, start, stop, ignore_properties=ignore_properties)).get())); 
    return pybind::item(reader::read_item(name, start, stop, ignore_properties=ignore_properties));
}
std::string pbreader::filename()
    { return reader::filename();}
std::string pbreader::groupname()
    { return reader::groupname();}
h5features::version pbreader::get_version()
    { return reader::version();}