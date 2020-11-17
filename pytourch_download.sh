#!/bin/bash
#SBATCH --cpus-per-task=6  # Cores proportional to GPUs: 6 on Cedar, 16 on Graham.
#SBATCH --mem=32G       # Memory proportional to GPUs: 32000 Cedar, 64000 Graham.
#SBATCH --time=0-03:00
#SBATCH --output=%N-%j.out
#SBATCH --gres=gpu:p100:1

module load python/3.6
virtualenv --no-download $SLURM_TMPDIR/env
source $SLURM_TMPDIR/env/bin/activate
module load python/3.6
pip install torch --no-index
pip install --no-index torch torchvision torchtext torchaudio
pip install --no-index transformers

# module load nixpkgs/16.09  gcc/7.3.0
# module load faiss/1.6.2
# curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
# pip install .
# pip install wget
# python data/download_data.py --resource data.wikipedia_split.psgs_w100
# python data/download_data.py --resource data.retriever.nq
# python data/download_data.py --resource data.retriever.qas.nq

python -m torch.distributed.launch \
	--nproc_per_node=6 train_dense_encoder.py \
	--max_grad_norm 2.0 \
	--encoder_model_type hf_bert \
	--pretrained_model_cfg bert-base-uncased \
	--seed 12345 \
	--sequence_length 256 \
	--warmup_steps 1237 \
	--batch_size 2 \
	--do_lower_case \
	--train_file "/home/ahamsala/projects/def-ehyangit/ahamsala/DPR/data/retriever/nq-train-subset.json" \
	--dev_file "/home/ahamsala/projects/def-ehyangit/ahamsala/DPR/data/retriever/nq-dev.json" \
	--output_dir "/home/ahamsala/projects/def-ehyangit/ahamsala/DPR/output" \
	--learning_rate 2e-05 \
	--num_train_epochs 1 \
	--dev_batch_size 16 \
 	--val_av_rank_start_epoch 1


python -m torch.distributed.launch \
	--nproc_per_node=1 train_dense_encoder.py \
	--max_grad_norm 2.0 \
	--encoder_model_type hf_bert \
	--pretrained_model_cfg bert-base-uncased \
	--seed 12345 \
	--sequence_length 256 \
	--warmup_steps 1237 \
	--batch_size 2 \
	--do_lower_case \
	--train_file "/home/ahamsala/projects/def-ehyangit/ahamsala/DPR/data/MSMARCO.dev.json" \
	--dev_file "/home/ahamsala/projects/def-ehyangit/ahamsala/DPR/data/retriever/nq-dev.json" \
	--output_dir "/home/ahamsala/projects/def-ehyangit/ahamsala/DPR/output" \
	--learning_rate 2e-05 \
	--num_train_epochs 1 \
	--dev_batch_size 16 \
 	--val_av_rank_start_epoch 1