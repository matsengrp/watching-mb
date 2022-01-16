#!/bin/bash

set -eu -o pipefail

# This parallelized version was too costly.
# ls analysis/ | parallel 'cd analysis/{} && wtch-run-analysis.sh'

for i in 1 3 7 8;
do
    cd analysis/ds$i
    wtch-run-analysis.sh
    cd ../..
done
