#!/bin/bash

set -eu

# A version of realpath that works on OSX, ensuring that the path has no
# spaces.
realpath_osx() {
    [[ $1 = /* ]] && echo "$1" || echo "$PWD/${1#./}"
}

for i in 1 3 4 5 6 7 8;
do
    for target in analysis golden;
    do
        mkdir -p $target/ds${i}
        data_path=$(realpath $target)/ds${i}/data
        test -e $data_path || ln -s $(realpath ds-data/ds${i}) $data_path
    done
    ln -s $(realpath_osx golden/ds${i}) $(realpath_osx analysis/ds${i}/golden)
done

# Install all scripts with the `wtch` prefix into the conda environment.
for script in scripts/wtch-*;
do
    test -e $CONDA_PREFIX/bin/$(basename $script) || ln -s $(realpath_osx $script) $CONDA_PREFIX/bin/
done
