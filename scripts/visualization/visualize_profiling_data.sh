#!/bin/bash

BUILD_DIR=$1

gprof ${BUILD_DIR}/MABE | gprof2dot -w | dot -Tpdf -o ${BUILD_DIR}/profiling_output.pdf
