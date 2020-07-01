#ifndef H5FEATURES_FEATURES_H
#define H5FEATURES_FEATURES_H

#include <vector>

namespace h5features
{
/**
   \brief The features class stores the features vectors of a `h5features::item`

   Each item's timestamp is associated to a features vector of constant
   dimension. Features are stored as float64 values.

 */
class features
{
public:
   // Lifecycle

   /// Destructor
   virtual ~features() = default;

   /**
      \brief Default constructor

      \warning Builds an invalid (empty) `features` instance
   */
   features() = default;

   /// Copy constructor
   features(const features&) = default;

   /// Move constructor
   features(features&&) = default;

   /// Copy operator
   features& operator=(const features&) = default;

   /// Move operator
   features& operator=(features&&) = default;

   /// @name Constructors
   /// @{
   /**
      \brief Constructs a `features` instance from features vectors

      \param data A vector of `size * dim` scalars, with `size` frames of `dim`
      scalars each
      \param dim The dimension of each frame
      \param check When true, ensures the features are valid

      \throw h5features::exception If `check` is true and the features are not valid

      \see h5features::features::validate

    */
   features(const std::vector<double>& data, std::size_t dim, bool check=true);
   features(std::vector<double>&& data, std::size_t dim, bool check=true);
   /// @}

   /// Returns true if the two `features` instances are equal
   bool operator==(const features& other) const noexcept;

   /// Returns true if the two `features` instances are not equal
   bool operator!=(const features& other) const noexcept;

   /// Returns the dimension of a features vector
   std::size_t dim() const;

   /// Returns the number of features vectors
   std::size_t size() const noexcept;

   /**
      \brief Throws a `h5features::exception` if the features are not valid

      The features are valid if and only if:
      - it is non empty (at least one features vector)
      - all the vectors have the same dimension

      \throw h5features::exception If the features are not valid

    */
   void validate() const;

   /**
      \brief Returns the features data

      The returned `data` is such as `data[i * dim() + j]` the \f$j^{th}\f$
      dimension of the \f$i^{th}\f$ frame.

    */
   const std::vector<double>& data() const noexcept;

private:
   // The stored features
   std::vector<double> m_features;

   // The features dimension
   std::size_t m_dim;
};
}

#endif  // H5FEATURES_FEATURES_H
