#include <reader.h>

pybind::reader::reader(const std::string& filename,const std::string& group) : h5features::reader::reader(filename, group) {}
pybind11::list pybind::reader::items() 
    {return pybind11::cast(h5features::reader::items());}
pybind::item pybind::reader::read(const std::string& name, bool ignore_properties) 
{
    
    // std::unique_ptr<pbitem> it =  std::unique_ptr<pbitem>(dynamic_cast<pbitem*>(std::make_unique<h5features::item>(reader::read_item(name, ignore_properties=ignore_properties)).get())); 
    return pybind::item(h5features::reader::read_item(name, ignore_properties=ignore_properties));
}
pybind::item pybind::reader::read_btw(const std::string& name, double start, double stop, bool ignore_properties)
{
    // std::unique_ptr<pbitem> it =  std::unique_ptr<pbitem>(dynamic_cast<pbitem*>(std::make_unique<h5features::item>(reader::read_item(name, start, stop, ignore_properties=ignore_properties)).get())); 
    return pybind::item(h5features::reader::read_item(name, start, stop, ignore_properties=ignore_properties));
}
std::string pybind::reader::filename()
    { return h5features::reader::filename();}
std::string pybind::reader::groupname()
    { return h5features::reader::groupname();}
h5features::version pybind::reader::get_version()
    { return h5features::reader::version();}