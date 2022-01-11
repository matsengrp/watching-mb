#!/bin/bash

set -eu -o pipefail

ls analysis/ | parallel 'cd analysis/{} && scripts/wtch-run-analysis.sh'
