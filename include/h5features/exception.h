#ifndef H5FEATURES_EXCEPTION_H
#define  H5FEATURES_EXCEPTION_H

#include <stdexcept>
#include <string>


namespace h5features
{
/// Defines an exception type to report errors from the h5features library.
class exception : public std::runtime_error
{
public:
   /// @name Constructors
   /// @{
   /// Constructs the exception with `what` as explanatory string
   explicit exception(const std::string& what);

   explicit exception(const char* what);
   /// @}
};
}

#endif  //  H5FEATURES_EXCEPTION_H
