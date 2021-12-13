#!/bin/bash

set -eu -o pipefail

REPO_ROOT="../.."
SCRIPTS_DIR=$REPO_ROOT/scripts/
TEMPLATE_DIR=$REPO_ROOT/templates/

$SCRIPTS_DIR/run-iqtree.sh

gpb template --template-dir ${TEMPLATE_DIR} mb-for-watching.json data/base.json config.json
python ${REPO_ROOT}/scripts/add-starting-tree.py
gpb template --template-dir ${TEMPLATE_DIR} basic.mb config.json run.mb

mb run.mb | tee mb.log

gpb template --template-dir ${TEMPLATE_DIR} process-watching-mb-run.sh config.json process-watching-mb-run.sh

sh process-watching-mb-run.sh

touch 0sentinel
