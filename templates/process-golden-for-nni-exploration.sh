set -eu

# This script prepares golden run data for explorying NNI subsplit DAG support.
# This expects to run at watching-mb/nni-analysis/ds{{ds_number}}.

# Convert the fasta file from the nexus file.
seqmagick convert data/DS{{ds_number}}.n.nex ds{{ds_number}}.fasta

# Create the newick files and csv of the pp values from the posterior pickle.
wtch-unpickle-cdf.py golden/mb/posterior.pkl ds{{ds_number}}.credible.nwk ds{{ds_number}}.mb-trees.nwk ds{{ds_number}}.mb-pp.csv  

# Generate all Nearest Neighbor Interchange trees of the credible set.
wtch-generate-all-nnis.sh ds{{ds_number}}.credible.nwk {{reroot_number}} > ds{{ds_number}}.neighbors.nwk

# Get optimal branches from iqtree. 
wtch-branch-optimization.py ds{{ds_number}}.neighbors.nwk ds{{ds_number}}.fasta ds{{ds_number}}.ordered.nwk --sort=True
wtch-branch-optimization.py ds{{ds_number}}.credible.nwk ds{{ds_number}}.fasta ds{{ds_number}}.credible.with-branches.nwk --sort=False
wtch-branch-optimization.py ds{{ds_number}}.mb-trees.nwk ds{{ds_number}}.fasta ds{{ds_number}}.mb-trees.with-branches.nwk --sort=False

# Reroot on {{reroot_number}}, which is {{reroot_name}}.
nw_reroot ds{{ds_number}}.ordered.nwk {{reroot_number}} > ds{{ds_number}}.rerooted.nwk
nw_reroot ds{{ds_number}}.credible.with-branches.nwk {{reroot_number}} > ds{{ds_number}}.credible.rerooted.nwk
nw_reroot ds{{ds_number}}.mb-trees.with-branches.nwk {{reroot_number}} > ds{{ds_number}}.mb-trees.rerooted.nwk

# Prepare and do the short MCMC run, which we'll compare against.
cd mcmc-explore 
./prepare-comparison-mcmc.sh 
cd ..

# Run reps_and_likelihoods to get the representations.
# Be warned, the following call may be too much to handle, even on the cluster.
rerooted1=ds{{ds_number}}.rerooted.nwk 
rerooted2=ds{{ds_number}}.credible.rerooted.nwk 
rerooted3=ds{{ds_number}}.mb-trees.rerooted.nwk
out1=ds{{ds_number}}.representations.csv 
out2=ds{{ds_number}}.credible.representations.csv 
out3=ds{{ds_number}}.mb-trees.representations.csv
# To make sure taxon ordering is the same, all files have the same first tree.
head -n 1 $rerooted1 > rerooted2
head -n 1 $rerooted1 > rerooted3
cat $rerooted2 >> rerooted2
cat $rerooted3 >> rerooted3
reps_and_likelihoods ds{{ds_number}}.fasta $rerooted1 $out1 rerooted2 out2 rerooted3 out3
tail -n +2 out2 > $out2
tail -n +2 out3 > $out3

# File cleanup.
rm mmapped_plv.data
rm rerooted2
rm rerooted3
rm out2
rm out3
