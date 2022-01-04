#!/bin/bash

set -eu -o pipefail

TEMPLATE_DIR=$WTCH_ROOT/templates/

mkdir iqtree && cd iqtree
wtch-run-iqtree.sh
cd ..

mkdir mb && cd mb
wtch-run-mb.sh ${TEMPLATE_DIR}
cd ..

mkdir sdag && cd sdag
wtch-run-sdag.sh
cd ..

touch 0sentinel
