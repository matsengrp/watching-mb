seq -w 0 199 | parallel 'iqtree -s ds1.fasta -m JC69 -pre iqtree_run{} -t RANDOM -seed {}'
cat *treefile | nw_reroot - 15 | nw_order - | nw_topology - | sort | uniq -c > counted_topologies.txt
rm *ckp.gz *log
