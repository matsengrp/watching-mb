gpb template --template-dir $1 mb-for-watching.json ../data/base.json config.json
python $2add-starting-tree.py
gpb template --template-dir $1 basic.mb config.json run.mb

mb run.mb | tee mb.log

gpb template --template-dir $1 process-watching-mb-run.sh config.json process-watching-mb-run.sh

sh $1process-watching-mb-run.sh
