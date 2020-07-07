#ifndef H5FEATURES_TEST_UTILS_CAPTURE_H
#define H5FEATURES_TEST_UTILS_CAPTURE_H

#include <iostream>
#include <boost/test/tools/output_test_stream.hpp>


namespace utils
{
/**
   A helper class to capture std::cout or std::cerr during tests

 */
class capture_stream
{
public:
   capture_stream(std::ostream& stream);
   ~capture_stream();

   bool is_equal(const std::string& message, bool flush=true);
   bool is_empty(bool flush=true);

private:
   std::ostream& m_stream;
   boost::test_tools::output_test_stream m_test_stream;
   std::streambuf* m_old;
};
}

#endif  //  H5FEATURES_TEST_UTILS_CAPTURE_H
