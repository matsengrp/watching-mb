# Prepare files for a golden MB run, and run.
set -eu

mkdir -p mb
cd mb

for i in 0 1 2 3 4 5 6 7 8 9;
do
    mkdir -p runs/a${i}
    cd runs/a${i}

    wtch-template.sh mb-for-golden.json ../../../data/base.json config.json
    seed=$(expr 42 + $i)
    wtch-json-attr-edit.py config.json config.json seed $seed

    wtch-template.sh simplest.mb config.json run.mb
    mb run.mb | tee mb.log &

    cd ../../
done

#will need to do processing after this. Need to glue files together, reroot, and all that....
