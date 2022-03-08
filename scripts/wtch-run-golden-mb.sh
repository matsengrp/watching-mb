# Prepare files for a golden MB run, and run.

set -eu

mkdir -p mb
cd mb

wtch-template.sh mb-for-golden.json ../data/base.json config.json
wtch-template.sh simplest.mb config.json run.mb

mb run.mb | tee mb.log

wtch-template.sh --mb process-golden-mb-run.sh config.json process-golden-mb-run.sh
sh process-golden-mb-run.sh
