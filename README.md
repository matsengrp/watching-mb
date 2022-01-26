# Pipeline for watching MrBayes

## Requirements

[Install bito](https://github.com/phylovi/bito), building a conda environment named `bito`

Additional dependencies that you can install in your `bito` environment using

    conda activate bito
    pip install -e .
    conda env update --file environment.yml

## Further setup, to be run in the root directory of the repository

    git submodule update --init --recursive
    make -C spr_neighbors
    conda env config vars set WTCH_ROOT=$PWD
    conda activate bito


## To run

Make sure you are first in the right conda environment.

### Set up directories and paths

    scripts/setup.sh

### Run the golden runs

    scripts/all-golden.sh

### Run analysis

    scripts/all-analysis.sh
