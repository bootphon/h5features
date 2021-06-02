#include <h5features/writer.h>
#include <pybind11/pybind11.h>
#include <h5features/version.h>
#include <pbitem.h>

class pbwriter : public h5features::writer
{
    public:
        pbwriter(
        const std::string& filename,
         const std::string& group = "features",
         bool overwrite= false,
         bool compress = true,
         h5features::version version=h5features::current_version
         );
        void write(pbitem item);
        h5features::version get_version();
};