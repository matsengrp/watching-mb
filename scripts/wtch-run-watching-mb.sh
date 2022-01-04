# Prepare files for a MB run, and run.

set -eu

wtch-template.sh mb-for-watching.json ../data/base.json config.json
wtch-add-starting-tree.py
wtch-template.sh basic.mb config.json run.mb

mb run.mb | tee mb.log

wtch-tempate.sh process-watching-mb-run.sh config.json process-watching-mb-run.sh

sh process-watching-mb-run.sh
