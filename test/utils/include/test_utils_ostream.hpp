#ifndef H5FEATURES_TEST_UTILS_OSTREAM_HPP
#define H5FEATURES_TEST_UTILS_OSTREAM_HPP

#include <h5features/features.h>
#include <h5features/item.h>
#include <h5features/properties.h>
#include <h5features/times.h>
#include <h5features/writer.h>
#include <boost/test/included/unit_test.hpp>
#include <iostream>
#include <vector>
#include <set>


BOOST_TEST_DONT_PRINT_LOG_VALUE(std::vector<std::vector<double>>)
BOOST_TEST_DONT_PRINT_LOG_VALUE(std::vector<h5features::item>)


namespace std
{
template<class T1, class T2>
std::ostream& boost_test_print_type(std::ostream& ostr, const std::pair<T1, T2>& v)
{
   ostr << v.first << ": " << v.second;
   return ostr;
}

template<class T>
std::ostream& boost_test_print_type(std::ostream& ostr, const std::vector<T>& v)
{
   ostr << "[";

   if(v.size() > 0)
   {
      ostr << v[0];
   }

   for(std::size_t i = 1; i < 5; ++i)
   {
      if(v.size() > i)
      {
         ostr << ", " << v[i];
      }
   }

   if(v.size() > 5)
   {
      ostr << ", ... " << v.size() - 5 << "more";
   }

   ostr << "]";

   return ostr;
}


template<class T>
std::ostream& boost_test_print_type(std::ostream& ostr, const std::set<T>& v)
{
   return boost_test_print_type(ostr, std::vector<T>(v.begin(), v.end()));
}


std::ostream& boost_test_print_type(std::ostream& ostr, const h5features::times& v)
{
   ostr << "times (" << v.size() << "): ["
        << v.start() << ", ..., " << v.stop() << "]";
   return ostr;
}


std::ostream& boost_test_print_type(std::ostream& ostr, const h5features::features& v)
{
   ostr << "features (" << v.size() << " x " << v.dim() << ")";
   return ostr;
}


std::ostream& boost_test_print_type(std::ostream& ostr, const h5features::properties& v)
{
   ostr << "properties (" << v.size() << "): ";
   boost_test_print_type(ostr, v.names());
   return ostr;
}


std::ostream& boost_test_print_type(std::ostream& ostr, const h5features::item& v)
{
   ostr << "item (" << v.name() << ",  " << v.dim() << ", " << v.size() << ")";
   return ostr;
}


std::ostream& boost_test_print_type(std::ostream& ostr, const h5features::writer& v)
{
   ostr << "writer (" << v.filename() << ",  " << v.groupname() << ")";
   return ostr;
}

}


#endif  // H5FEATURES_TEST_UTILS_OSTREAM_HPP
