#include "h5features/version.h"
#include "nanobind/nanobind.h"

namespace nb = nanobind;

void init_version(nb::module_ &m) {
  nb::enum_<h5features::version>(m, "Version",
                                 "The different h5features format versions.\n\n This is **not** the version of the "
                                 "h5features library but the available\n versions of the underlying file format.")
      .value("v1_0", h5features::version::v1_0)
      .value("v1_1", h5features::version::v1_1)
      .value("v1_2", h5features::version::v1_2)
      .value("v2_0", h5features::version::v2_0);
}
