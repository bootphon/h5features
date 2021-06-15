#include <read_group.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace pybind
{
    pybind11::list read_group(std::string f_name)
    {
       return pybind11::cast(h5features::read_group(f_name));
    }
}

void init_read_group(pybind11::module& m)
{
    m.def("read_group", &pybind::read_group);
}