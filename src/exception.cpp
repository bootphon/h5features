#include <h5features/exception.h>

h5features::exception::exception(const std::string& what_arg)
   : std::runtime_error(what_arg)
{}


h5features::exception::exception(const char* what_arg)
   : std::runtime_error(what_arg)
{}
