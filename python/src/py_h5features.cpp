#include "nanobind/nanobind.h"

namespace nb = nanobind;

void init_version(nb::module_ &m);
void init_item(nb::module_ &m);
void init_reader(nb::module_ &m);
void init_writer(nb::module_ &m);

NB_MODULE(_core, m) {
  init_version(m);
  init_item(m);
  init_reader(m);
  init_writer(m);
}
