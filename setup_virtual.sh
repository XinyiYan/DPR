#!/bin/bash

module load python/3.6.3

# Replace virtual_DPR with where ever you create your virtual env.
virtualenv --no-download virtual_DPR
source virtual_DPR/bin/activate

pip install torch --no-index
pip install --no-index torch torchvision torchtext torchaudio
pip install --no-index transformers
pip install spacy[cuda] --no-index

module load nixpkgs/16.09 gcc/7.3.0 cuda/10.1
export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH

module load python/3.6.3
module load faiss/1.6.2
deactivate

source virtual_DPR/bin/activate
python --version
