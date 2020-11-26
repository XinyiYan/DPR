#!/bin/bash
#SBATCH --cpus-per-task=1  # Cores proportional to GPUs: 6 on Cedar, 16 on Graham.
#SBATCH --mem=32G       # Memory proportional to GPUs: 32000 Cedar, 64000 Graham.
#SBATCH --time=0-03:00
#SBATCH --output=%N-%j.out


module load python/3.6.3
mkdir input_data # Make directory to store all input data
mkdir json_data  # Make directory to store all json outputted data

# Download collection (~2.9 GB)
#wget https://msmarco.blob.core.windows.net/msmarcoranking/collection.tar.gz # USED for both TREC CAsT and MSMARCO data creations

https://msmarco.blob.core.windows.net/msmarcoranking/collectionandqueries.tar.gz
tar xzf collectionandqueries.tar.gz

# CAR Collection (largest)
wget http://trec-car.cs.unh.edu/datareleases/v2.0/paragraphCorpus.v2.0.tar.xz
tar xf paragraphCorpus.v2.0.tar.xz

# Download qid -> query (~42 MB)
wget https://msmarco.blob.core.windows.net/msmarcoranking/queries.tar.gz
tar xzf queries.tar.gz

# MARCO duplicate file (id:[dup list of ids])
wget http://boston.lti.cs.cmu.edu/Services/treccast19/duplicate_list_v1.0.txt

#qrel file (uid=utterance id, junk, pid, score) (.tsv)
wget https://raw.githubusercontent.com/daltonj/treccastweb/master/2019/data/training/train_topics_mod.qrel

# Last file we need is raw_utterance_allennlp_tell_me (uid, query) (.tsv)
# Upload this seperately (small file) Look for notebook Nicole made or data in shared google drive.

# Hopefully we can pip install... yikes..
pip install cbor
pip install trec-car-tools

# Create JSON for MSMARCO data set
python MSMARCO_JSON_NoNeg.py \
  --output_dir json_data/ \ 	           # Location desired for output of json data. (check mkdir at start)
  --input_dir input_Data/ \	           # Location of where data that was downloaded is stored (check mkdir at start)
  --qrel_filename qrels.dev.small.tsv \    # swap for qrels.train.tsv if desired for complete training dataset
  --query_filename queries.dev.tsv         # swap for queries.train.tsv for complete training dataset

# Create JSON for TREC CAsT data set
python TREC_CAsT_JSON_NoNeg.py \
  --output_dir json_data/ \ #
  --input_dir input_data/ \
  --car_collection input_data/ \
  --score_threshold 2

python train_val_split_json.py \
  --output_path_name "json_data/merged5050" \
  --trec_path_name "json_data/TREC_CAsT.json" \
  --msmarco_path_name "json_data/MSMARCO.dev.json" \ # Swap .dev. AND .train. as needed.
  --trec_train_pct 80 \
  --msmarco_train_pct 80 \
  --trec_test_pct 10 \
  --msmarco_test_pct 10
