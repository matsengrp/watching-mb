set -eu

# This expects to run at watching-mb/nni-analysis/ds{{ds_number}}.
wtch-nni-likelihood-walk.py ds{{ds_number}}.representations.csv ds{{ds_number}}.nni-walk.representations.csv --max_tree_ratio=0.01
# Decrease the ratio for a faster run.
