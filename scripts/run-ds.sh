#!/bin/bash

set -eu -o pipefail

REPO_ROOT="../../.."
SCRIPTS_DIR=$REPO_ROOT/scripts/
TEMPLATE_DIR=$REPO_ROOT/templates/

mkdir iqtree && cd iqtree
${SCRIPTS_DIR}run-iqtree.sh
cd ..

mkdir mb && cd mb
${SCRIPTS_DIR}run-mb.sh ${TEMPLATE_DIR} ${SCRIPTS_DIR}
cd ..

touch 0sentinel
