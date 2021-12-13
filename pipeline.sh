#!/bin/bash

set -eu -o pipefail

scripts/setup.sh
ls analysis/ | parallel 'cd analysis/{} && ../../scripts/run-ds.sh'
