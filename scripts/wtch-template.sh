# Perform `wmb template`, but with the right template directory.

set -eu

wmb template --template-dir $WTCH_ROOT/templates/ $@
