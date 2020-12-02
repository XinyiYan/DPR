#!/bin/bash
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH --time=0-05:00:00
#SBATCH --output=%N-%j.out

module load python/3.6.3
virtualenv --no-download $SLURM_TMPDIR/DPR
source $SLURM_TMPDIR/DPR/bin/activate
module load StdEnv/2020
module load scipy-stack/2020b


pip install cbor
pip install trec-car-tools

mkdir ctx_files  # Make directory to store all collections which are ctx_data
cd ctx_files

# CAR Collection (largest)
wget http://trec-car.cs.unh.edu/datareleases/v2.0/paragraphCorpus.v2.0.tar.xz 
tar xf paragraphCorpus.v2.0.tar.xz

cd ..

time python partition_car.py \
--ctx_files_dir "ctx_files/"

sbatch merge-job.sh
# zip -r ctx_collection.zip ctx_files/paragraphCorpus
# cp ctx_collection.zip /home/pmcw/projects/def-aghodsib/pmcw