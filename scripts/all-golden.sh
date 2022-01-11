#!/bin/bash

set -eu -o pipefail

ls golden/ | parallel 'cd golden/{} && wtch-run-golden-mb.sh'
