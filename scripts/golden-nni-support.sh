#!/bin/bash

# This script prepares the golden run datasets for exploring the NNI support. The main 
# steps for this are handled by a templated script, process_golden_for_exploration.sh, 
# which this script prepares to run for each of the individual datasets. This script is
# meant to run from the top-level watching-mb directory.


set -eu

for i in 1 3 4 5 6 7 8;
do
    cd nni-analysis/ds${i}

    template_name=process-golden-for-exploration.sh
    wtch-template.sh $template_name ../data/base.json $template_name

    # For now we don't run the created script. For DS1, this may (or may not) work on a
    # local machine and will work on the cluster, but the other datasets run out  memory 
    # even on the cluster.
    #sh $template_name

    # Prepare for the next iteration.
    cd ../../../
done
