#!/bin/bash

set -eu -o pipefail

ls analysis/ | parallel 'cd analysis/{} && ../../scripts/run-ds.sh'
