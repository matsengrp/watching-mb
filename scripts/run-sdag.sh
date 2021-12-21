#!/bin/bash

python $1pickle-cdf.py ../mb/rerooted-topology-sequence.tab golden.pickle
python $1generate-sdag-trees.py ../mb/rerooted-topology-sequence.tab sdag-trees.nwk golden.pickle
nw_topology sdag-trees.nwk| nw_order - > sdag-topologies.nwk
