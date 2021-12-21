#!/bin/bash

set -eu -o pipefail

seqmagick convert ../data/*.n.nex ds.fasta
iqtree -s ds.fasta -m JC69
