#!/bin/bash

set -eu -o pipefail

# This MrBayes run will take several days to a week.
cd golden/ds1 
wtch-run-golden-mb-big.sh

cd mb
wtch-template.sh process-trprobs.sh ../data/base.json process-trprobs.sh
chmod +x process-trprobs.sh
./process-trprobs.sh
