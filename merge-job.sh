#!/bin/bash
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH --time=0-00:10:00
#SBATCH --output=%N-%j.out

module load python/3.6.3
virtualenv --no-download $SLURM_TMPDIR/DPR
source $SLURM_TMPDIR/DPR/bin/activate

#Things you may want to change:
# output_path_name: Just change the name at end like the example (merged_data)
# msmarco_path_name: Probably will switch between .dev. and .train.
# the remaining 4 all all about the splits
time python train_val_split_json.py \
--output_path_name json_data/merged_data \
--trec_path_name json_data/TREC_CAsT.json \
--msmarco_path_name json_data/MSMARCO.dev.json \
--trec_train_pct 80 \
--msmarco_train_pct 80 \
--trec_test_pct 10 \
--msmarco_test_pct 10