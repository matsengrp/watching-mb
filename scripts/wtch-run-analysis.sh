#!/bin/bash

set -eu -o pipefail

mkdir iqtree && cd iqtree
wtch-run-iqtree.sh
cd ..

mkdir mb && cd mb
wtch-run-watching-mb.sh
cd ..

wtch-investigate-watching-mb.py

touch 0sentinel
