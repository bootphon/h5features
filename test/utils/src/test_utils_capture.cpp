#include "test_utils_capture.h"

#include <string>

utils::capture_stream::capture_stream(std::ostream &stream)
    : m_stream{stream}, m_test_stream{}, m_old(m_stream.rdbuf(m_test_stream.rdbuf())) {}

utils::capture_stream::~capture_stream() { m_stream.rdbuf(m_old); }

bool utils::capture_stream::is_equal(const std::string &message, bool flush) {
  return m_test_stream.is_equal(message, flush);
}

bool utils::capture_stream::contains(const std::string &message, bool flush) {
  const std::string stream = m_test_stream.str();

  if (flush) {
    m_test_stream.flush();
  }

  return stream.find(message) != std::string::npos;
}

bool utils::capture_stream::is_empty(bool flush) { return m_test_stream.is_empty(flush); }
