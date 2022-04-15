#!/bin/bash
# Output all NNIs of the trees in a given file.

set -eu -o pipefail

if test $# -ne 2; then
    echo "Please supply a newick file of trees for which we can generate all NNI neighbors, and the taxon id to use for rerooting."
    exit 1
fi

tree_path="$1"
root_taxon="$2"

temp_file=$(mktemp)
trap "rm -f $temp_file" 0 2 3 15

cat "$tree_path" | while read line
do
    echo $line | spr_neighbors --nni >> $temp_file
done

cat $temp_file | nw_reroot - $root_taxon | nw_order - | sort -R | uniq
