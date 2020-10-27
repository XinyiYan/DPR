#!/bin/bash
#SBATCH --cpus-per-task=1  # Cores proportional to GPUs: 6 on Cedar, 16 on Graham.
#SBATCH --mem=32G       # Memory proportional to GPUs: 32000 Cedar, 64000 Graham.
#SBATCH --time=0-03:00
#SBATCH --output=%N-%j.out
#SBATCH --account=def-ehyangit # adjust this to match the accounting group you are using to submit jobs
#SBATCH --job-name=DPR

module load python/3.6

virtualenv --no-download $SLURM_TMPDIR/env
source $SLURM_TMPDIR/env/bin/activate
pip install torch --no-index
pip install --no-index torch torchvision torchtext torchaudio
pip install wget


module load python/3.6
module load nixpkgs/16.09  gcc/7.3.0
module load faiss/1.6.2


pip install .

python data/download_data.py --resource data.wikipedia_split.psgs_w100
python data/download_data.py --resource data.retriever.nq
python data/download_data.py --resource data.retriever.qas.nq

