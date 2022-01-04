# Perform `gpb template`, but with the right template directory.

set -eu

gpb template --template-dir $WTCH_ROOT/templates/ $@

