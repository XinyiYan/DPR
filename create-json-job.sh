#!/bin/bash
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH --time=0-05:00:00
#SBATCH --output=%N-%j.out

module load StdEnv/2020
module load scipy-stack/2020b
module load python/3.6.3
virtualenv --no-download $SLURM_TMPDIR/DPR
source $SLURM_TMPDIR/DPR/bin/activate
module load StdEnv/2020
module load scipy-stack/2020b


pip install cbor
pip install trec-car-tools

# Makes all these from location where sbatch "shellfile" is called
mkdir input_data # Make directory to store all input data except collections
mkdir json_data  # Make directory to store all json outputted data
mkdir ctx_files  # Make directory to store all collections which are ctx_data

cp raw_utterance_allennlp_tell_me input_data

cd ctx_files
# CAR Collection (largest)
wget http://trec-car.cs.unh.edu/datareleases/v2.0/paragraphCorpus.v2.0.tar.xz 
tar xf paragraphCorpus.v2.0.tar.xz

cd ..

cd input_data

# get MSMARCO collection
wget https://msmarco.blob.core.windows.net/msmarcoranking/collectionandqueries.tar.gz
tar xzf collectionandqueries.tar.gz

# MARCO duplicate file (id:[dup list of ids])
wget http://boston.lti.cs.cmu.edu/Services/treccast19/duplicate_list_v1.0.txt

# qrel file (uid=utterance id, junk, pid, score) (.tsv)
wget https://raw.githubusercontent.com/daltonj/treccastweb/master/2019/data/training/train_topics_mod.qrel

cd ..

# copy collection.tsv to ctx_files since this will be zipped and sent later
cp input_data/"collection.tsv" ctx_files

# CAN RUN ANYTHING IN SAME DIRECTORY ASLONG AS: sbatch NAME.sh
# qrel_filename: change between qrels.dev.small.tsv and qrels.train.tsv
# query_filename: queries.dev.tsv and queries.train.tsv
time python MSMARCO_JSON_NoNeg.py  \
--output_dir "json_data/" \
--input_dir "input_data/" \
--qrel_filename "qrels.dev.small.tsv" \
--query_filename "queries.dev.tsv"

time python TREC_CAsT_JSON_NoNeg.py \
--output_dir "json_data/" \
--input_dir "input_data/" \
--ctx_files_dir "ctx_files/" \
--score_threshold "2"

sbatch merge-job.sh
# zip -r ctx_collection.zip ctx_files/paragraphCorpus
# cp ctx_collection.zip /home/pmcw/projects/def-aghodsib/pmcw
