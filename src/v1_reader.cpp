#include "h5features/details/v1_reader.h"
#include "h5features/details/properties_reader.h"
#include "h5features/exception.h"
#include <algorithm>
#include <iostream>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

/*
 * Because of a bug in HighFive when reading string datasets wrote from h5py, we
 * need a custom low-level function to read that. Here we assume the dataset has
 * a single dimension.
 */
std::vector<std::string> read_string_dataset(const hdf5::DataSet dataset) {
  // retrieve the ID of the dataset
  hid_t dataset_id = dataset.getId();

  // retrieve the type of items
  hid_t datatype_id = H5Tcopy(dataset.getDataType().getId());

  // read the number of items stored (assuming a single dimension)
  hsize_t nitems;
  hid_t space_id = H5Dget_space(dataset_id);
  H5Sget_simple_extent_dims(space_id, &nitems, NULL);

  // allocate memory to store the items and read them
  char **raw_data = new char *[nitems];
  H5Dread(dataset_id, datatype_id, H5S_ALL, H5S_ALL, H5P_DEFAULT, raw_data);

  // convert it to a vector of strings
  std::vector<std::string> items(nitems);
  for (size_t i = 0; i < nitems; ++i) {
    items[i] = std::string(raw_data[i]);
  }

  // deallocate raw data
  H5Dvlen_reclaim(datatype_id, space_id, H5P_DEFAULT, raw_data);
  delete[] raw_data;

  H5Dclose(dataset_id);
  H5Sclose(space_id);
  H5Tclose(datatype_id);

  return items;
}

h5features::v1::reader::reader(hdf5::Group &&group, h5features::version version)
    : h5features::details::reader_interface{std::move(group), version} {
  std::string items_dataset_name;
  std::string index_dataset_name;
  switch (m_version) {
  case h5features::version::v1_1:
  case h5features::version::v1_2:
    items_dataset_name = "items";
    index_dataset_name = "index";
    break;
  case h5features::version::v1_0:
    items_dataset_name = "files";
    index_dataset_name = "file_index";
    break;
  default:
    std::stringstream msg;
    msg << "unsupported h5features format version " << m_version;
    throw h5features::exception(msg.str());
    break;
  }

  try {
    m_items = read_string_dataset(m_group.getDataSet(items_dataset_name));
    m_group.getDataSet(index_dataset_name).read(m_index);
  } catch (const hdf5::Exception &e) {
    // failed to load the datasets, assumes the group is empty (this is
    // required to have a behavior consistent with version 2.0)
    m_items.clear();
    m_index.clear();
  }
}

std::vector<std::string> h5features::v1::reader::items() const { return m_items; }

h5features::item h5features::v1::reader::read_item(const std::string &name, bool ignore_properties) const {
  // retrieve the start and stop indices of the item in the index
  const auto position = get_item_position(name);

  // read the item
  return {name, {read_features(position)}, {read_times(position)}, {read_properties(name, ignore_properties)}, false};
}

h5features::item h5features::v1::reader::read_item(const std::string &name, double start, double stop,
                                                   bool ignore_properties) const {
  // retrieve the start and stop indices of the item in the index
  const auto position = get_item_position(name);

  // retrieve the sub-position from times
  const auto times = read_times(position);
  const auto subposition = times.get_indices(start, stop);

  return {name,
          read_features({position.first + subposition.first, position.first + subposition.second}),
          times.select(subposition.first, subposition.second),
          {read_properties(name, ignore_properties)},
          false};
}

std::pair<std::size_t, std::size_t> h5features::v1::reader::get_item_position(const std::string &name) const {
  // ensure the item exists
  const auto item_iterator = std::find(m_items.begin(), m_items.end(), name);
  if (item_iterator == m_items.end()) {
    throw h5features::exception("the requested item does not exist: " + name);
  }

  const auto index = std::distance(m_items.begin(), item_iterator);
  if (index != 0) {
    return {m_index[index - 1] + 1, m_index[index] + 1};
  } else {
    return {0, m_index[0] + 1};
  }
}

h5features::features h5features::v1::reader::read_features(const std::pair<std::size_t, std::size_t> &position) const {
  try {
    const auto dataset = m_group.getDataSet("features");
    const auto dim = dataset.getDimensions()[1];
    std::vector<double> data(dim * (position.second - position.first));
    dataset.select({position.first, 0}, {position.second - position.first, dim}).read_raw(data.data());
    return {data, dim, false};
  } catch (const std::exception &e) {
    throw h5features::exception(std::string("failed to read features: ") + e.what());
  }
}

h5features::times h5features::v1::reader::read_times(const std::pair<std::size_t, std::size_t> &position) const {
  // retrieve the name of the times dataset according to file version
  std::string times_name;
  switch (m_version) {
  case h5features::version::v1_1:
  case h5features::version::v1_2:
    times_name = "labels";
    break;
  default:
    times_name = "times";
  }

  try {
    const auto dataset = m_group.getDataSet(times_name);
    const auto dim = dataset.getDimensions().size();
    const auto size = position.second - position.first;
    std::vector<double> data(dim * size);
    dataset.select({position.first, 0}, {size, dim}).read_raw(data.data());
    return {data, h5features::times::get_format(dim), false};
  } catch (const std::exception &e) {
    throw h5features::exception(std::string("failed to read times: ") + e.what());
  }
}

h5features::properties h5features::v1::reader::read_properties(const std::string &name, bool ignore_properties) const {
  // warn user if properties are present but not readable
  if (m_version <= h5features::version::v1_1 and m_group.exist("properties") and not ignore_properties) {
    std::cerr << "WARNING h5features version " << m_version << ": ignoring properties while reading item " << name
              << std::endl;
  } else if (m_group.exist("properties") and not ignore_properties) {
    const hdf5::Group properties_group = m_group.getGroup("properties");
    if (properties_group.exist(name)) {
      const hdf5::Group item_group = properties_group.getGroup(name);
      return h5features::details::read_properties(item_group);
    }
  }
  return {};
}
