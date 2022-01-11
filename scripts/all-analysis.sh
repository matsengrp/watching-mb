#!/bin/bash

set -eu -o pipefail

ls analysis/ | parallel 'cd analysis/{} && wtch-run-analysis.sh'
