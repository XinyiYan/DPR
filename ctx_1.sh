#!/bin/bash
#SBATCH --cpus-per-task=1  # Cores proportional to GPUs: 6 on Cedar, 16 on Graham.
#SBATCH --mem=32G       # Memory proportional to GPUs: 32000 Cedar, 64000 Graham.
#SBATCH --time=0-06:0:00
#SBATCH --output=%N-%j.out
#SBATCH --gres=gpu:p100:1


module load python/3.6.3
virtualenv --no-download $SLURM_TMPDIR/torch_DPR
source $SLURM_TMPDIR/torch_DPR/bin/activate
module load python/3.6.3
pip install torch --no-index
pip install --no-index torch torchvision torchtext torchaudio
pip install --no-index transformers==3.0.2
pip install spacy[cuda] --no-index
module load nixpkgs/16.09  gcc/7.3.0  cuda/10.1
export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH
module load python/3.6.3
module load faiss/1.6.2
deactivate
source $SLURM_TMPDIR/torch_DPR/bin/activate

# mkdir data/checkpoint
# wget https://dl.fbaipublicfiles.com/dpr/checkpoint/retriver/multiset/hf_bert_base.cp data/checkpoint


mkdir data/embedding_1



time python generate_dense_embeddings.py \
  --model_file 'data/checkpoint/hf_bert_base.cp' \
  --ctx_file '/ctx_file/CAR_collection_1.tsv' \
  --shard_id  1 \
  --num_shards 10\
  --batch_size 128 \
  --out_file 'data/embedding_1'
