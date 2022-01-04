#!/bin/bash

python wtch-pickle-cdf.py ../mb/rerooted-topology-sequence.tab golden.pickle
python wtch-generate-sdag-trees.py ../mb/rerooted-topology-sequence.tab sdag-trees.nwk golden.pickle
nw_topology sdag-trees.nwk| nw_order - > sdag-topologies.nwk
