#!/bin/bash

cd ./analysis

for i in $(seq 8);
do
    cd ds$i
    mkdir iqtree
    mv ds.fasta* iqtree
    cd ..
done