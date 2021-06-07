#include <h5features/details/writer_interface.h>


h5features::details::writer_interface::writer_interface(
   hdf5::Group&& group, bool compress, h5features::version version)
   : m_group{std::move(group)}, m_compress{compress}, m_version{version}
{}


h5features::details::writer_interface::~writer_interface()
{}


h5features::version h5features::details::writer_interface::version() const noexcept
{
   return m_version;
}
