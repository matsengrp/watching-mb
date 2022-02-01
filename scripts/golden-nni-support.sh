#!/bin/bash

# This script prepares the golden run datasets for exploring the NNI support.
# The main steps for this are handled by a templated script, 
# process_golden_for_exploration.sh, which this script prepares to run for each
# of the individual datasets.
# This script is meant to run from the top-level watching-mb directory.


set -eu

for i in 1 3 4 5 6 7 8;
do
    # Create directory, if it doesn't already exist, and move there.
    mkdir -p golden/ds${i}/posterior-support
    cd golden/ds${i}/posterior-support

    # Create a shell file based on the template.
    template_name=process-golden-for-exploration.sh
    wtch-template.sh $template_name ../data/base.json $template_name

    # For now we don't run the created script. For DS1, this may work on a 
    # local machine, but will work on the cluster. The other datasets run out
    # of memory even on the cluster.
    #sh $template_name

    # Prepare ready for the next iteration.
    cd ../../../
done
