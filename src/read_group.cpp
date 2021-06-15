#include <string>
#include <vector>
#include <read_group.h>
std::vector<std::string> h5features::read_group(std::string f_name)
{
    return HighFive::File(f_name).listObjectNames();
}
