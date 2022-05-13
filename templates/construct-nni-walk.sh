set -eu

# This expects to run at watching-mb/nni-analysis/ds{{ds_number}}.
sdag_rep_path=ds{{ds_number}}.representations.csv
output_path=ds{{ds_number}}.nni-walk.representations.csv
extra_trees_path=ds{{ds_number}}.extra-trees.representations.csv
if [[ -f $extra_trees_path && -s $extra_trees_path ]]
then
  wtch-nni-likelihood-walk.py $sdag_rep_path $output_path --extra_trees_path=$extra_trees_path --max_tree_ratio=0.01
else
  wtch-nni-likelihood-walk.py $sdag_rep_path $output_path --max_tree_ratio=0.01
fi
# Decrease the ratio for a faster run.
