import sys
from os import remove
from os.path import exists
from timeit import Timer
import pytest
from unittest import TestCase
import h5features as h5f
sys.path.insert(0, "./h5features2")
from item import Item
from writer import Writer
from reader import Reader
import tracemalloc
# from pyh5features import Item , Writer, Reader
import numpy as np
# from memory_profiler import profile
import time
def data():
    n=10000
    size = 100
    dim = 10
    items =["item"+str(i) for i in range(n)]
    features = [np.array(np.random.rand(size, dim) , dtype=np.float64) for _ in range(n)]
    times = [np.asarray([i+0.5 for i in range(size) ], dtype=np.float64)for _ in range(n)]
    begin = np.asarray([i for i in range(size)], dtype=np.float64)
    end = np.asarray([i+1 for i in range(size)], dtype=np.float64)
    properties = {}
    print(len(items), len(features), len(times))
    return (items, features, times, properties, begin, end, n)



@profile
def unw(items, features, times, properties, begin, end,n):
    def _unw():
        if exists("testone.h5"):
            remove("testone.h5")
        objet = h5f.Data(items, times, features, check=True)
        with h5f.writer.Writer("testone.h5", version="1.1") as writer:
            writer.write(objet, "group1")
        return objet
    return _unw()
@profile
def deuxw(items, features, times, properties, begin, end,n):
    def _deuxw():
        if exists("testtwo.h5f"):
            remove("testtwo.h5f")
        writer = Writer("testtwo.h5f", "group1", False, False, "2.0")
        for i in range(n):
            objet= Item.create(items[i], features[i], (begin, end), properties)
        
            writer.write(objet)
        return objet
    return _deuxw()
@profile
def unr(items, features, times, properties, begin, end,n):
    def _unr():
        l =[]
        reader = h5f.reader.Reader("testone.h5", "group1")
        l=reader.read(from_item="item"+str(0) , to_item="item"+str(n-1))
        return l
    return _unr()
    # print(w.features()[0].shape)
    # print(rdata.features()[0].shape)
@profile
def deuxr(items, features, times, properties, begin, end,n):
    def _deuxr():
        l=[]
        reader=Reader("testtwo.h5f", "group1")
        for it in items:
            l.append(reader.read(it, False))
        return l
    return _deuxr()
@profile
def unrbtw(items, features, times, properties, begin, end,n):
    def _unrbtw():
        return h5f.reader.Reader("testone.h5", "group1").read(from_item="item"+str(0), to_item="item"+str(n-1), from_time=0, to_time=1000000)
    return _unrbtw()
@profile
def deuxrbtw(items, features, times, properties, begin, end,n):
    def _deuxrbtw():
        l=[]
        reader=Reader("testtwo.h5f", "group1")
        for it in items:
            l.append(reader.read(it, features_between_times=(0, 1000000), ignore_properties=False))
        return l
    return _deuxrbtw()

items, features, times, properties, begin, end, n = data()
a= unw(items, features, times, properties, begin, end,n)
a = np.asarray(a.features())
print(a.shape)
a=deuxw(items, features, times, properties, begin, end,n)
a = np.asarray(a.features())
print(a.shape)
a=unr(items, features, times, properties, begin, end,n)
a = np.asarray(a.features())
print(a.shape)
a=deuxr(items, features, times, properties, begin, end,n)
a = np.asarray([i.features() for i in a])
print(a.shape)
a=unrbtw(items, features, times, properties, begin, end,n)
a = np.asarray(a.features())
print(a.shape)
a=deuxrbtw(items, features, times, properties, begin, end,n)
a = np.asarray([i.features() for i in a])
print(a.shape)