#include "h5features/reader.h"
#include "nanobind/nanobind.h"
#include "nanobind/stl/filesystem.h"
#include "nanobind/stl/string.h"
#include "nanobind/stl/vector.h"
#include <filesystem>
#include <string>

namespace nb = nanobind;
using namespace nb::literals;

void init_reader(nb::module_ &m) {
  nb::class_<h5features::reader>(m, "Reader")
      .def(
          "__init__",
          [](h5features::reader *t, const std::filesystem::path &filename, const std::string &group) {
            return new (t) h5features::reader(filename.string(), group);
          },
          "filename"_a, nb::kw_only(), "group"_a = "features", "Read :py:class:`.Item` instances from an HDF5 file.")
      .def(
          "read",
          [](const h5features::reader &self, const std::string &name, bool ignore_properties) {
            return self.read_item(name, ignore_properties);
          },
          "name"_a, nb::kw_only(), "ignore_properties"_a = false, "Read an :py:class:`.Item` from the HDF5 file.")
      .def(
          "read_partial",
          [](const h5features::reader &self, const std::string &name, double start, double stop,
             bool ignore_properties) { return self.read_item(name, start, stop, ignore_properties); },
          "name"_a, "start"_a, "stop"_a, nb::kw_only(), "ignore_properties"_a = false,
          "Partial read of an :py:class:`.Item` within the time interval ``[start, stop]``.")
      .def("read_all", &h5features::reader::read_all, nb::kw_only(), "ignore_properties"_a = false,
           "Read all the items stored in the file.")
      .def("items", &h5features::reader::items, "The name of stored items.")
      .def_prop_ro("filename", &h5features::reader::filename, "The name of the file being read.")
      .def_prop_ro("groupname", &h5features::reader::groupname, "The name of the group being read in the file.")
      .def_prop_ro("version", &h5features::reader::version,
                   "The :py:class:`.Version` of the h5features data in the group.")
      .def_static(
          "list_groups",
          [](const std::filesystem::path &filename) { return h5features::reader::list_groups(filename.string()); },
          "filename"_a, "Return the list of groups in the specified HDF5 file.")
      .def("__repr__", [](const h5features::reader &self) {
        return nb::str("Reader(filename={}, groupname={})").format(self.filename(), self.groupname());
      });
}
