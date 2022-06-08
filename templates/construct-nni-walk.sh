set -eu

# This expects to run at watching-mb/nni-analysis/ds{{ds_number}}.

# Call as ./construct-nni-walk.sh --use_parsimony to use parsimony scores instead of likelihoods.
sdag_rep_path=ds{{ds_number}}.representations.csv
nwk_path=ds{{ds_number}}.topologies.nwk
fasta_path=ds{{ds_number}}.fasta
output_path=ds{{ds_number}}.nni-walk.representations.csv
extra_trees_path=ds{{ds_number}}.extra-trees.representations.csv

extra_parameters=""
if [[ -f $extra_trees_path && -s $extra_trees_path ]]
then
        extra_parameters=$extra_parameters"--extra_trees_path="$extra_trees_path" "
fi
if [[ $# != 0 ]]
then
        extra_parameters=$extra_parameters$1
fi

wtch-nni-likelihood-walk.py $sdag_rep_path $output_path --max_tree_ratio=0.01 --nwk_path=$nwk_path --fasta_path=$fasta_path $extra_parameters
# Decrease the ratio for a faster run.
