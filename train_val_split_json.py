import argparse
import json
import random

def train_test_split(args,trec_data, msmarco_data):

  trec_size = len(trec_data)
  msmarco_size = len(msmarco_data)

  trec_test_size = int(trec_size * float((float(args.trec_test_pct)/100.0)))
  msmarco_test_size = int(msmarco_size * float((float(args.msmarco_test_pct)/100.0)))

  trec_train_size = int(trec_size * float((float(args.trec_train_pct)/100.0)))
  msmarco_train_size = int(msmarco_size * float((float(args.msmarco_train_pct)/100.0)))

  # Get testing data prepared
  merged_test_data = []
  trec_test_samples = random.sample(range(trec_size), trec_test_size)
  for idx in trec_test_samples:
      merged_test_data.append(trec_data[idx])

  msmarco_test_samples = random.sample(range(msmarco_size), msmarco_test_size)
  for idx in msmarco_test_samples:
      merged_test_data.append(msmarco_data[idx])

  # Get training data prepared
  merged_train_data = []
  temp1 = set(trec_test_samples) ^ set(range(trec_size)) # train + val
  trec_train_samples = random.sample(list(temp1), trec_train_size)
  for idx in trec_train_samples:
      merged_train_data.append(trec_data[idx])
  temp2 = set(msmarco_test_samples) ^ set(range(msmarco_size)) # train + val set
  
  
  msmarco_train_samples = random.sample(list(temp2), msmarco_train_size)
  for idx in msmarco_train_samples:
      merged_train_data.append(msmarco_data[idx])

  # Get validation data prepared
  merged_val_data = []
  trec_val_samples = set(trec_train_samples) ^ set(temp1)
  for idx in trec_val_samples:
      merged_val_data.append(trec_data[idx])

  msmarco_val_samples = set(msmarco_train_samples) ^ set(temp2)
  for idx in msmarco_val_samples:
      merged_val_data.append(msmarco_data[idx])

  # Write to files
  filename = args.output_path_name # path + filename (i.e. /home/pmcw/projects/DPR/data/MSMARCO)
  with open(filename + '.test' + '.json', 'w') as json_file:
      json.dump(merged_test_data, json_file)

  with open(filename + '.train' + '.json', 'w') as json_file:
      json.dump(merged_train_data, json_file)

  with open(filename + '.val' + '.json', 'w') as json_file:
      json.dump(merged_val_data, json_file)
  return None


def main():
    parser = argparse.ArgumentParser()

    # Grab output directory from user
    parser.add_argument("--output_path_name", default="", type=str,
                        help="Output file path and name of desired file")

    # Grab trec data file name and path
    parser.add_argument("--trec_path_name", default="", type=str,
                        help="Location and name of TREC CAsT json file")

    # Grab msmarco data file name and path
    parser.add_argument("--msmarco_path_name", default="", type=str,
                        help="Location and name of MSMARCO json file")

    # Grab trec test size as integer
    parser.add_argument("--trec_train_pct", default=50, type=int,
                        help="Percent of data train size will be")

    # Grab msmarco test size as integer
    parser.add_argument("--msmarco_train_pct", default=50, type=int,
                        help="Percent of data train size will be")

    # Grab trec test size as integer
    parser.add_argument("--trec_test_pct", default=50, type=int,
                        help="Percent of data test size will be")

    # Grab msmarco test size as integer
    parser.add_argument("--msmarco_test_pct", default=50, type=int,
                        help="Percent of data test size will be")



    args = parser.parse_args()  # Make them reachable

    with open(args.trec_path_name) as f:
        trec_data = json.load(f)

    with open(args.msmarco_path_name) as f:
        msmarco_data = json.load(f)

    train_test_split(args, trec_data, msmarco_data)


if __name__ == "__main__":
    main()