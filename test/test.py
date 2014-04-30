# -*- coding: utf-8 -*-
"""
Created on Wed Apr 30 09:59:57 2014

@author: Thomas Schatz
"""

import h5features as feat
import numpy as np
import os


try:
    # write
    features_0 = np.random.randn(300, 20)
    times_0 = np.linspace(0, 2, 300) 
    feat.simple_write('test.h5', 'features_0', times_0, features_0)
    
    n_files = 30
    features = []
    times = []
    files = []
    for i in range(n_files):
        n_frames = np.random.randint(400)+1
        features.append(np.random.randn(n_frames, 20))
        times.append(np.linspace(0, 2, n_frames))  
        files.append('File %d' % (i+1))
    feat.write('test.h5', 'features', files, times, features)
    
    # concatenate to existing dataset
    features_added_1 = np.zeros(shape=(1, 20))
    times_added_1 = np.linspace(0, 2, 1) 
    feat.write('test.h5', 'features', ['File 31'], [times_added_1], [features_added_1])
    features_added_2 = np.zeros(shape=(2, 20))
    times_added_2 = np.linspace(0, 2, 2) 
    feat.write('test.h5', 'features', ['File 31'], [times_added_2], [features_added_2])
    
    # read
    times_0_r, features_0_r = feat.read('test.h5', 'features_0')
    assert times_0_r.keys() == ['features']
    assert features_0_r.keys() == ['features']
    assert all(times_0_r['features'] == times_0)
    assert all(features_0_r['features'] == features_0)
    
    times_r, features_r = feat.read('test.h5', 'features')
    assert set(times_r.keys()) == set(files+['File 31'])
    assert set(features_r.keys()) == set(files+['File 31'])
    for i, f in  enumerate(files):
        assert all(times_r[f] == times[i])
        assert all(features_r[f] == features[i])
    assert all(times_r['File 31'] == np.concatenate([times_added_1, times_added_2]))
    assert all(features_r['File 31'] == np.concatenate([features_added_1, features_added_2], axis=0))  
    #FIXME test smaller reads    
    
finally:
    os.remove('test.h5')

    