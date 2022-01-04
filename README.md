# Pipeline for watching MrBayes

## Requirements

* https://github.com/phylovi/bito : this will build a conda environment named `bito`
* https://github.com/matsengrp/gp-benchmark-1-environment/ : clone and install with `pip install .`
* https://pypi.org/project/seqmagick/
* https://www.gnu.org/software/parallel/ (available via https://anaconda.org/conda-forge/parallel)
* https://github.com/tjunier/newick_utils
* http://nbisweden.github.io/MrBayes/

You can install all of these in your `bito` environment using

    conda activate bito
    conda env update --file environment.yml

## Further setup, to be run in the root directory

    git submodule update --init --recursive
    conda env config vars set WTCH_ROOT=$PWD
    conda activate bito


## To run

Make sure you are first in the right conda environment.

    scripts/setup.sh
    ./pipeline.sh
