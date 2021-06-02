#!/bin/bash
kernprof -l test/python/python_test/performances_test.py 
python3 -m line_profiler performances_test.py.lprof 
python3 -m memory_profiler test/python/python_test/performances_test.py 