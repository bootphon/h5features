#include "h5features/details/reader_interface.h"
#include <utility>

h5features::details::reader_interface::reader_interface(hdf5::Group &&group, h5features::version version)
    : m_group{std::move(group)}, m_version(version) {}

h5features::details::reader_interface::~reader_interface() {}

h5features::version h5features::details::reader_interface::version() const noexcept { return m_version; }
