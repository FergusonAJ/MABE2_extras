#!/bin/bash
gprof $1/MABE | gprof2dot -n 5 | dot -Tpdf -o profiling_data.pdf 
