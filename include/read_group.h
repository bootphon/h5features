#include <string>
#include <vector>
#include <h5features/hdf5.h>

namespace h5features
{
    /**
    \brief returns a list of groups in the hdf5 file specified

    \param name the name of hdf5 file

     */
    std::vector<std::string> read_group(std::string f_name);
}


