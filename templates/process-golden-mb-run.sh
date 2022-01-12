set -eu

# rerooting on {{reroot_number}}, which is {{reroot_name}}
awk '$1~/tree/ {print $NF}' {{output_prefix}}.t | nw_topology - | nw_reroot - {{reroot_number}} | nw_order - \
    | tail -n +{{burnin_samples}} > rerooted-topologies.noburnin.nwk
sort rerooted-topologies.noburnin.nwk | uniq -c | sort -nr | sed -e "s/^[ ]*//" -e "s/ /  /" > rerooted-topologies.noburnin.counted.nwk
TREE_COUNT=$(awk '{sum+=$1} END{print sum;}' rerooted-topologies.noburnin.counted.nwk)
awk '{sum+=$1; print $1/'${TREE_COUNT}' "  " sum/'${TREE_COUNT}' "  " $0}' rerooted-topologies.noburnin.counted.nwk | column -t > rerooted-topologies.noburnin.posterior.nwk

wtch-pickle-cdf.py rerooted-topologies.noburnin.posterior.nwk ../posterior.pkl
wtch-dag-stats-of-pickle-cdf.py ../posterior.pkl ../dag-stats.json
