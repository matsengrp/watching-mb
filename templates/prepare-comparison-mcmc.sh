#!/bin/bash

set -eu -o pipefail

# This expects to run at watching-mb/nni-analysis/ds{{ds_number}}/mcmc-explore.


#Take the max likelihood tree from the credible set and NNI neighbors. Technically this 
#might not be the same tree we start the NNI walk with, but for that to happen the SDAG
#would need to have a better tree than all of the credible set and the immediate NNI
#neighbors (these are the trees used to generate the SDAG), which is unlikely.
#We make and write to the iqtree directory, so that we can call the existing 
#functionality of wtch-run-watching-mb.sh without any edits.
mkdir -p iqtree && cd iqtree
head -n 1 ../nni-analysis/ds{{ds_number}}.ordered.nwk > ds.fasta.treefile
cd ..

mkdir -p mb && cd mb
wtch-run-watching-mb.sh
cd ..
