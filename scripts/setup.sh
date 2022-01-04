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
    data_path=analysis/ds${i}/data
    test ! -e $data_path || ln -s $(realpath_osx ds-data/ds${i}) $data_path
done

for i in scripts/wtch-*;
do
    ln -s $(realpath_osx $i) $CONDA_PREFIX/bin/
done
