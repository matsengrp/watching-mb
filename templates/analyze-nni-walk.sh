set -eu

# This expects to run at watching-mb/nni-analysis/ds{{ds_number}}.

nni_rep_path=ds{{ds_number}}.nni-walk.representations.csv
cred_rep_path=ds{{ds_number}}.credible.representations.csv
pp_rep_path=ds{{ds_number}}.mb-trees.representations.csv
pp_values_path=ds{{ds_number}}.mb-pp.csv
golden_pickle_path=golden/posterior.pkl
topology_sequence_path=analysis/mb/rerooted-topology-sequence.tab
wtch-investigate-nni-walk.py $nni_rep_path $cred_rep_path $pp_rep_path $pp_values_path $golden_pickle_path $topology_sequence_path
