# Pipeline for watching MrBayes

## Requirements

* https://github.com/phylovi/bito : install in a conda environment as per the instructions
* https://github.com/matsengrp/gp-benchmark-1-environment/ : clone and install with `pip install .`
* https://pypi.org/project/seqmagick/
* https://www.gnu.org/software/parallel/ (available via https://anaconda.org/conda-forge/parallel)
* https://github.com/tjunier/newick_utils
* http://nbisweden.github.io/MrBayes/



    conda env update --file environment.yml

## Further setup

    git submodule update --init --recursive


## To run

    ./pipeline.sh
