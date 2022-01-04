#!/bin/bash

set -eu

mkdir -p analysis

realpath_osx() {
    [[ $1 = /* ]] && echo "$1" || echo "$PWD/${1#./}"
}

for i in $(seq 8);
do
    mkdir -p analysis/ds${i}
    # Ensure current path has no spaces
    ln -s $(realpath_osx ds-data/ds${i}) analysis/ds${i}/data
done
