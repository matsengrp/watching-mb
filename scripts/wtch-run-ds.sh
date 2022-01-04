#!/bin/bash

set -eu -o pipefail

mkdir iqtree && cd iqtree
wtch-run-iqtree.sh
cd ..

mkdir mb && cd mb
wtch-run-watching-mb.sh
cd ..

mkdir sdag && cd sdag
wtch-run-sdag.sh
cd ..

touch 0sentinel
