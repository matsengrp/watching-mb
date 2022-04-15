#!/bin/bash

set -eu -o pipefail

mkdir -p iqtree && cd iqtree
wtch-run-iqtree.sh
cd ..

mkdir -p mb && cd mb
wtch-run-watching-mb.sh
cd ..

wtch-investigate-watching-mb.py

touch 0sentinel
