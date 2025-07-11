#include "h5features/item.h"
#include "h5features/version.h"
#include "h5features/writer.h"
#include "nanobind/nanobind.h"
#include "nanobind/stl/filesystem.h"
#include "nanobind/stl/string.h"
#include "nanobind/stl/vector.h"
#include <filesystem>
#include <string>
#include <vector>

namespace nb = nanobind;
using namespace nb::literals;

void init_writer(nb::module_ &m) {
  nb::class_<h5features::writer>(m, "Writer")
      .def(
          "__init__",
          [](h5features::writer *t, std::filesystem::path &filename, const std::string &group, bool overwrite,
             bool compress, h5features::version version) {
            return new (t) h5features::writer(filename.string(), group, overwrite, compress, version);
          },
          "filename"_a, nb::kw_only(), "group"_a = "features", "overwrite"_a = false, "compress"_a = false,
          "version"_a = h5features::current_version, "Write :py:class:`.Item` instances to an HDF5 file.")
      .def(
          "write", [](h5features::writer &self, const h5features::item &item) { return self.write(item); }, "item"_a,
          "Write an :py:class:`.Item` to disk.")
      .def(
          "write",
          [](h5features::writer &self, const std::vector<h5features::item> &items) {
            return self.write(items.begin(), items.end());
          },
          "items"_a, "Write a sequence of :py:class:`.Item` to disk in parallel.")
      .def_prop_ro("version", &h5features::writer::version, "The h5features format :py:class:`.Version` being written.")
      .def_prop_ro("filename", &h5features::writer::filename, "The HDF5 file name.")
      .def_prop_ro("groupname", &h5features::writer::groupname, "The HDF5 group name.")
      .def("__repr__", [](const h5features::writer &self) {
        return nb::str("Writer(filename={}, groupname={})").format(self.filename(), self.groupname());
      });
}
