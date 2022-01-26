#!/bin/bash
# Output all NNIs of the trees in a given file.

set -eu -o pipefail

if test $# -ne 1; then
    echo "Please supply a newick file of trees for which we can generate all NNI neighbors."
    exit 1
fi

temp_file=$(mktemp)
trap "rm -f $temp_file" 0 2 3 15

cat "$1" | while read line
do
    echo $line | spr_neighbors --nni >> $temp_file
done

nw_order $temp_file | sort -R | uniq
