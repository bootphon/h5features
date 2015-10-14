"""Test of the h5features2.writer module.

@author: Mathieu Bernard
"""


from utils import remove, assert_raise
from h5features2.writer import Writer, parse_filename

class TestParseFilename:
    """Test _check_file method."""

    def setup(self):
        self.filename = 'test.h5'

    def teardown(self):
        remove(self.filename)

    def test_no_file(self):
        assert_raise(parse_filename,
                     '/path/to/non/existant/file',
                     'No such file')

    def test_no_hdf5_file(self):
        with open(self.filename, 'w') as temp:
            temp.write('This is not a HDF5 file')

        assert_raise(parse_filename,
                     self.filename,
                     'not a HDF5 file')

    def test_good_file(self):
        parse_filename(self.filename)
