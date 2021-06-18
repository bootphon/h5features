#include <pybind11/pybind11.h>
#include <h5features/version.h>


void init_version(pybind11::module& m)
{
   pybind11::enum_<h5features::version>(m, "VersionWrapper")
      .value("v1_0", h5features::version::v1_0)
      .value("v1_1", h5features::version::v1_1)
      .value("v1_2", h5features::version::v1_2)
      .value("v2_0", h5features::version::v2_0)
      .export_values();
}
