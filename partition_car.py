import argparse
import json
import csv
import os
from trec_car import read_data
import re

def partition_CAR(args):
    placeholder_out = ''  # REPLACE WITH ARGS
    cbor_file = 'paragraphCorpus/dedup.articles-paragraphs.cbor'

    # Will fill files until they have 2e9 Bytes
    i = 0  # Starting index for files
    num_bytes = 3e9  # Just for initialization
    size_threshold = 2e9  # Number of bytes to signal creation of new output .tsv file

    for para in read_data.iter_paragraphs(open(args.ctx_files_dir + cbor_file, 'rb')):
        if num_bytes >= size_threshold:
            i += 1  # Will start at 1
            print(i)
            print(num_bytes)
            if i >= 2:
                out_file.close()  # Close the file that surpassed size_threshold
            else:
                pass
            out_file = open(args.ctx_files_dir + 'CAR_collection_{}.tsv'.format(i), 'wt',
                            encoding='utf-8')  # Needed to add encoding
            tsv_writer = csv.writer(out_file, delimiter='\t')

        # Write to file
        tsv_writer.writerow(['CAR' + '_' + para.para_id, ' '.join(para.get_text().split())])  # ["CAR_PID", "passage"]

        num_bytes = os.path.getsize(args.ctx_files_dir + 'CAR_collection_{}.tsv'.format(i))

    return None


def main():
    parser = argparse.ArgumentParser()


    # Grab location for car collection and where partitions will be written to
    parser.add_argument("--ctx_files_dir", default="", type=str,
                        help="The directory where paragraphCorpus/dedup.articles-paragraphs.cbor resides")

    args = parser.parse_args()

    # Partition the CAR collection
    partition_CAR(args)  # Create splits of CAR_collection_X

if __name__ == "__main__":
    main()
