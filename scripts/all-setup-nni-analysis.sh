#!/bin/bash

# This script is meant to run from the top-level watching-mb directory.

# This script prepares the golden run datasets for exploring the NNI support. The main 
# steps for this are handled by a templated scripts: process_golden_for_exploration.sh,
# construct-nni-walk.sh, and analyze-nni-walk.sh. For now, we only create these scripts
# in the appropriate directories. We don't run them in this script because
# process_golden_for_exploration.sh and analyze-nni-walk.sh take awhile to run and can
# easily run out of memory.

set -eu

for i in 1 3 4 5 6 7 8;
do
    cd nni-analysis/ds${i}

    t_name1=process-golden-for-nni-exploration.sh 
    t_name2=construct-nni-walk.sh 
    t_name3=analyze-nni-walk.sh
    for template_name in $t_name1 $t_name2 $t_name3;
    do	    
        wtch-template.sh $template_name data/base.json $template_name
    done

    cd ../../
done
