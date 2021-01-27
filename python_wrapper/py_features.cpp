#include <h5features/features.h>
#include <pybind11/pybind11.h>
#include <pybind11/operators.h>

void init_features(pybind11::module& m)
{

   pybind11::class_<h5features::features>(m, "Features", pybind11::buffer_protocol())
      .def(pybind11::init([](
            const pybind11::buffer & features ,
         std::size_t dim,
            bool check = true
         ){
         pybind11::buffer_info info = features.request();
         double *p = (double*)info.ptr;
         std::size_t size = features.request().size;
         auto  array = std::vector<double>(p, p+size);
         return h5features::features (array, dim, check);
      }))
      .def("dim", &h5features::features::dim, "returns the dimension of a feature vector")
      .def("size", &h5features::features::size, "returns the number of features vectors")
      .def("__eq__", &h5features::features::operator==, pybind11::is_operator(), "returns true if the two features instances are equal")
      .def("__ne__", &h5features::features::operator!=, pybind11::is_operator(), "returns true if the two features instances are not equal")      
      .def_buffer( [](h5features::features &features ) -> pybind11::buffer_info {
         double* p=(double*)features.data().data();
         return  pybind11::buffer_info(
            p,
            sizeof(double),
            pybind11::format_descriptor<double>::format(),
            2, {features.dim(),
            features.size()},
            {sizeof(double)*(int)features.size(),
            sizeof(double)});
      });
}
