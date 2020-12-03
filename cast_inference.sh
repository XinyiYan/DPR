#!/bin/bash
#SBATCH --cpus-per-task=1  # Cores proportional to GPUs: 6 on Cedar, 16 on Graham.
#SBATCH --mem=32G       # Memory proportional to GPUs: 32000 Cedar, 64000 Graham.
#SBATCH --time=0-02:0:00
#SBATCH --output=%N-%j.out
#SBATCH --gres=gpu:p100:1


# Change to where you make your virtual environment
module load python/3.6.3
source virtual_DPR/bin/activate



time python cast_dense_retriever.py \
  --model_file 'data/checkpoint/hf_bert_base.cp' \
  --ctx_file 'ctx_file/CAR_collection_X.tsv' \
  --qa_file '../treccastweb/2019/data/evaluation/evaluation_topics_annotated_resolved_v1.0.tsv' \
  --encoded_ctx_file 'data/collection_X_embedding*' \
  --out_file 'predictions/DPR_prediction_car_collection_X' \
  --n-docs 200