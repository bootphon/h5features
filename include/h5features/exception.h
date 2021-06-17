#ifndef H5FEATURES_EXCEPTION_H
#define H5FEATURES_EXCEPTION_H

#include <stdexcept>
#include <string>


namespace h5features
{
/// Defines an exception type to report errors from the h5features library.
class exception : public std::runtime_error
{
public:
   /// Constructs the exception with `what` as explanatory string
   template<typename String>
   explicit exception(String&& what)
      : std::runtime_error(std::forward<String>(what))
   {}
};
}

#endif  // H5FEATURES_EXCEPTION_H
