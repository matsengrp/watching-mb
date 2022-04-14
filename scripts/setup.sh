#!/bin/bash

set -eu

# A version of realpath that works on OSX, ensuring that the path has no
# spaces.
realpath_osx() {
    [[ $1 = /* ]] && echo "$1" || echo "$PWD/${1#./}"
}

# Install all scripts with the `wtch` prefix into the conda environment.
for script in scripts/wtch-* spr_neighbors/spr_neighbors;
do
    test -e $CONDA_PREFIX/bin/$(basename $script) || ln -s $(realpath_osx $script) $CONDA_PREFIX/bin/
done

for i in 1 3 4 5 6 7 8;
do
    for target in analysis golden nni-analysis mcmc-explore;
    do
        mkdir -p $target/ds${i}
        data_path=$(realpath $target)/ds${i}/data
        test -e $data_path || ln -s $(realpath ds-data/ds${i}) $data_path
    done
    ln -sfn $(realpath_osx golden/ds${i}) $(realpath_osx analysis/ds${i}/golden)
    ln -sfn $(realpath_osx golden/ds${i}) $(realpath_osx nni-analysis/ds${i}/golden)
    ln -sfn $(realpath_osx nni-analysis/ds${i}) $(realpath_osx mcmc-explore/ds${i}/nni-analysis)
    ln -sfn $(realpath_osx mcmc-explore/ds${i}) $(realpath_osx nni-analysis/ds${i}/mcmc-explore) 
done
