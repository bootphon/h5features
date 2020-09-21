#ifndef H5FEATURES_TIMES_H
#define H5FEATURES_TIMES_H

#include <vector>


namespace h5features
{
/**
   \brief The times class handles the timestamps of an item

   The times are expressed in second as float64 values.

   Each features frame in an item is associated to a timestamp. It can have one
   of the two following formats:

   - `times::format::simple` where the timestamp is a single scalar and is
     interpreted as the center of the frame's time window

   - `times::format::interval` where the timestamp is a pair `(tstart, tstop)`
     interpreted as the begin and end of the frame's time window.

*/
class times
{
public:
   /// The available times formats, `simple` is 1d and `interval` is 2d
   enum class format{simple, interval};

   /// Returns the times format from its dimension
   static format get_format(const std::size_t& dim);

   // Lifecyle

   /// Copy constructor
   times(const times&) = default;

   /// Move constructor
   times(times&&) = default;

   /// Copy operator
   times& operator=(const times&) = default;

   /// Move operator
   times& operator=(times&&) = default;

   /// Destructor
   virtual ~times() = default;

   /// @name Constructors
   /// @{
   /**
      \brief Constructs a `times` instance from raw data

      The times are expressed in seconds as float64 values.

      - If `times_format == times::format::simple`, the timestamps have a single
      dimension and each timstamp is interpreted as the center time of its
      associated frame. In that case `data[i]` is the center time of the frame
      `i`.

      - If `times_format == times::format::interval` there is two timestamps per
      frame, interpreted as the `(tstart, tstop)` times for each frame. Here
      `data[2*i]` and `data[2*i+1]` are the start and stop time of
      the frame `i` respectively.

      \param data The timestamps data
      \param times_format The actual format of the data
      \param validate When true, ensures the timestamps are valid

      \throw h5features::exception When `validate` is true, if the timestamps
      are not valid.

      \see h5features::times::validate

    */
   times(const std::vector<double>& data, format times_format, bool validate=true);
   times(std::vector<double>&& data, format times_format, bool validate=true);
   /// @}

   /**
      \brief Contructs a `times` instance from start and stop timestamps

      The built `times` instance has the `times::format::interval` format

      \param start The start timestamps of each frame
      \param stop The stop timestamps of each frame
      \param validate When true, ensures the timestamps are valid

      \throw h5features::exception If `start.size() != stop.size()`
      \throw h5features::exception When `validate` is true, if the timestamps
      are not valid.

      \see h5features::times::validate

    */
   times(const std::vector<double>& start, const std::vector<double>& stop, bool validate=true);

   /// Returns true if the two `times` instances are equal
   bool operator==(const times& other) const noexcept;

   /// Returns true if the two `times` instances are not equal
   bool operator!=(const times& other) const noexcept;

   /// Returns the size (number of frames) of the timestamps
   std::size_t size() const noexcept;

   /// Returns the timestamps dimension (1 or 2)
   std::size_t dim() const noexcept;

   /// Returns the timestamps raw data
   const std::vector<double>& data() const noexcept;

   /**
      \brief Returns the first timestamp
      \throw h5features::exception If times is empty
   */
   double start() const;

   /**
      \brief Returns the last timestamp
      \throw h5features::exception If times is empty
   */
   double stop() const;

   /**
      \brief Throws a `h5features::exception` if the timestamps are not valid

      The timestamps are valid if and only if:
      - `size() != 0`
      - sorted in increasing order
      - when `times::format::interval`, we have \f$tstart_i \leq tstop_i\f$ for
        each frame \f$i\f$

      \throw h5features::exception If the timestamps are not valid

   */
   void validate() const;

   /**
      \brief Returns the indices ``[i, j]`` of the closest timestamps to ``[start, stop]``

      This method is used by `h5features::item` for partial reads of features.

      \param start The start time to get the index from
      \param stop The stop time to get the index from

      \throw h5features::exception If `start` is greater than `stop`
      \throw h5features::exception If there is not valid indices for the
      requested interval

      \see h5features::reader
   */
   std::pair<std::size_t, std::size_t> get_indices(double start, double stop) const;

   /**
      \brief Returns a subset of those timestamps from `start` to `stop`

      \param start The first index of the returned times
      \param stop The last index of the returned times

      \throw h5features::exception If `start > stop` or `stop > size()`

   */
   times select(const std::size_t& start, const std::size_t& stop) const;

private:
   // Default constructor not used
   times() = delete;

   // The stored timestamps
   std::vector<double> m_data;

   // the timestamps format
   format m_format;
};
}

#endif  // H5FEATURES_TIMES_H
