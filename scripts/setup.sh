set -eu

mkdir -p analysis

for i in $(seq 8);
do
    mkdir -p analysis/ds${i}
    ln -s $(readlink -f ds-data/ds${i}) analysis/ds${i}/data
done
