# -*- coding: utf-8 -*-
"""
Created on Thu Jul 11 11:06:06 2013

@author: Thomas Schatz
"""

"""
function read_features

inputs:

- filename (hdf5 file potentially serving as a container for many small files)
- group
- (optional) from_internal_file (defaults to the first stored file)
- (optional) to_internal_file (defaults to from_internal_file if it was specified and to the last stored file otherwise)
- (optional) from_time, to_time (defaults to the beginning time in from_internal_file and the ending time in to_internal_file respectively)
        the specified times are included in the output
- (optional) index (for faster access)

outputs:
- features (a 2D array with the 'feature' dimension along the columns and the 'time' dimension along the lines)

Note that all the files that are present on disk between file1 and file2 will be loaded and returned by read_features. It's the responsibility 
of the user to make sure that it will fit into RAM memory.  

Also note that the functions are not concurrent nor thread-safe (because the HDF5 library is not concurrent and not always thread-safe), 
moreover, they aren't even atomic for independent process (because there are several independent calls to the file system), so that
thread-safety and atomicity of operation should be enforced externally.
"""

#FIXME write the write_index function: adapt also the read to correct the following shortcomings of the matlab version (and if possible also correct the matlab version):
#   - internal filenames could be encoded directly as string using a variable length dtype
#   - do the index-related datasets really neeed to be chunked ?
#   - the type of the various datasets do not seem currently adapted to the data (float for times for example), which is probably wasteful in terms of memory
#   - check if the choice of time along lines and feature along columns is optimal
# maintain compatibility by using a flag indicating the version ?

import h5py
import numpy as np

def read_features_index(filename, group):
    with h5py.File(filename, 'r') as f:
        g = f[group]
        files = ''.join([unichr(int(c)) for c in g['files'][...]]).replace('/-', '/').split('/\\') # parse unicode to strings
        index = {'files': files, 'file_index': np.int64(g['file_index'][...]), 'times': g['times'][...], 'format': g.attrs['format']} # file_index contains the index of the end of each file
        #FIXME ideally the type conversions above should be removable        
        if index['format'] == 'sparse':
            index['dim'] = g.attrs['dim'] #FIXME type ?
            index['lines'] = g['lines'][...] #FIXME type ?
    return index
    
#FIXME add default for group for both functions: check if only one group and take it otherwise fail 
def read_features(filename, group, from_internal_file=None, to_internal_file=None, from_time=None, to_time=None, index=None):    
    # parse arguments and find read coordinates   
    if index is None: index = read_features_index(filename, group)
    if to_internal_file is None:
        if from_internal_file is None:
            to_internal_file = index['files'][-1]
        else:
            to_internal_file=from_internal_file
    if from_internal_file is None:
        from_internal_file = index['files'][0]
    try: f1 = index['files'].index(from_internal_file) # the second 'index' in this expression refers to the 'index' method of class list
    except ValueError: raise Exception('No entry for file %s in %s\\%s' % (from_internal_file, filename, group))
    try: f2 = index['files'].index(to_internal_file)
    except ValueError: raise Exception('No entry for file %s in %s\\%s' % (to_internal_file, filename, group))
    f1_start = 0 if f1==0 else index['file_index'][f1-1] + 1 # index associated with the beginning of from_internal_file
    f1_end = index['file_index'][f1]    
    f2_start = 0 if f2==0 else index['file_index'][f2-1] + 1
    f2_end = index['file_index'][f2] # index associated with the end of to_internal_file  
    # could check that f2 is after f1 in the file
    if from_time is None: i1 = f1_start
    else:
        times = index['times'][f1_start:f1_end+1] # the end is included...                     
        i1 = f1_start + np.where(times>=from_time)[0][0]# smallest time larger or equal to from_time
        # here could catch exception if from_time is larger than the biggest time in from_external_time 
    if to_time is None: i2 = f2_end        
    else:
        times = index['times'][f2_start:f2_end+1] # the end is included...
        i2 = f2_start + np.where(times<=to_time)[0][-1]# largest time smaller or equal to to_time
        # here could catch exception if to_time is smaller than the smallest time in to_external_time 
    # access file
    with h5py.File(filename, 'r') as f:
        g = f[group]
        if index['format'] == 'dense':
            features = g['features'][:,i1:i2+1] # i2 included
            times = g['times'][i1:i2+1]
        else: #FIXME implement this
            raise IOError('reading sparse features not yet implemented')
    if f2>f1:
        file_ends = index['file_index'][f1:f2]-f1_start
        features = np.split(features, file_ends+1, axis=1)
        times = np.split(times, file_ends+1)
    else:
        features = [features] #FIXME maybe here keep not a list if to_internal_file was None and from_internal_file was not None (i.e. the user expects only the content of one specific file ?)
        times = [times]
    files = index['files'][f1:f2+1]
    features = dict(zip(files, features))
    times = dict(zip(files, times))
    return features, times
