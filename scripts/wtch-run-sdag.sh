#!/bin/bash

set -eu -o pipefail

wtch-generate-sdag-trees.py ../mb/rerooted-topology-sequence.tab sdag-trees.nwk ../golden/posterior.pkl
nw_topology sdag-trees.nwk | nw_order - > sdag-topologies.nwk
