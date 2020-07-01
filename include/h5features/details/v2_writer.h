#ifndef H5FEATURES_V2_WRITER_H
#define H5FEATURES_V2_WRITER_H

#include <h5features/details/writer_interface.h>


namespace h5features
{
namespace v2
{
class writer : public h5features::details::writer_interface
{
public:
   writer(hdf5::Group&& group, bool compress, h5features::version version);

   void write(const h5features::item& item) override;
};
}
}

#endif  // H5FEATURES_V2_WRITER_H
