import argparse
import json
import csv
import os
from trec_car import read_data
import re

def create_dup_dict(args):
    # document sotraged with paragraph idea no prefix of collection name.
    dup_file = "duplicate_list_v1.0.txt"
    lines = open(args.input_dir + dup_file).readlines()
    dup_dict = {}  # Store names of duplicates here

    for line in lines:
        data = line.strip().split(':')
        if len(data[1]) > 0:
            dup_docs = data[-1].split(',')
            for docs in dup_docs:
                dup_dict[docs] = 1

    return dup_dict  # {id:1}

def create_pid_2_pass(args,dup_dict):

    lines = open(args.input_dir + "collection.tsv", encoding='utf-8').readlines()  # Use to be collection.tsv
    pid_2_pass = {}  # pid -> passage

    # Create our pid_2_passage dictionary
    for line in lines:
        id, passage = line.strip().split('\t')
        col_ID = 'MARCO' + '_' + id
        if col_ID not in dup_dict:  # Only add MARCO passages that are not duplicates
            pid_2_pass[col_ID] = passage.rstrip()
        else:
            continue
    # Write the collection.tsv to folder with CAR_partitions
    return pid_2_pass

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
        tsv_writer.writerow(['CAR' + '_' + para.para_id, para.get_text()])  # ["CAR_PID", "passage"]

        num_bytes = os.path.getsize(args.ctx_files_dir + 'CAR_collection_{}.tsv'.format(i))

    return None

def seperate_qrel(args):
    # Split qrel into a list of CAR and MARCO passages then will
    # link to each of these individually
    marco_scored = []  # store MARCO lines here
    car_scored = []  # store CAR lines here
    placeholder_in = ""  # REPLACE WITH ARGS

    scored_passages = open(args.input_dir + "train_topics_mod.qrel", 'r').readlines()
    # Code to splits scored passages into a MARCO and CAR set
    for idx, line in enumerate(scored_passages):
        uid, _, doc_id, score = line.strip().split()
        if bool(re.search('MARCO', doc_id)):  # MARCO
            marco_scored.append(line)
        elif bool(re.search('CAR', doc_id)):
            car_scored.append(line)
        else:
            pass  # Don't want any WAPO

    return marco_scored, car_scored  # [line,...] for each

def search_marco_qrel(marco_scored, marco_p2p, uid_2_pid):
    # Find marco passages
    for data in marco_scored:
        doc_id = data.split()[2].strip()  # looking for this
        uid = data.split()[0].strip()  # utterance id
        score = data.split()[3].strip()  # score
        pid = str(doc_id)  # MSMARCO_ID

        if doc_id == 'MARCO_4286598':
            continue  # This is a duplicate that has a scoring
        else:
            pass

        if uid not in uid_2_pid:
            uid_2_pid[uid] = [(pid, marco_p2p[pid], score)]
        else:
            uid_2_pid[uid] += [(pid, marco_p2p[pid], score)]

    return None

def search_car_qrel(args,car_scored, uid_2_pid):
    # Find car passages

    # Get CAR scored passages
    for i in range(1, 8):  # Spark would be better here
        CAR_data = open(args.ctx_files_dir + 'CAR_collection_{}.tsv'.format(i)).readlines()

        # Create dict for doc_id -> index in current file then use index -> passage
        CAR_dict = {}
        for idx, line in enumerate(CAR_data):
            doc_id = line.split('\t')[0].strip()
            CAR_dict[doc_id] = idx

        print('On CAR {} partition'.format(i))
        for data in car_scored:  # Loop over CAR scored passages
            doc_id = data.split()[2].strip()  # looking for this
            uid = data.split()[0].strip()  # utterance id
            score = data.split()[3].strip()  # score
            pid = str(doc_id)  # MSMARCO_ID
            if doc_id in CAR_dict:  # Is in this partition?
                if uid not in uid_2_pid:
                    uid_2_pid[uid] = [
                        (pid, ' '.join([text.strip() for text in CAR_data[CAR_dict[doc_id]].split('\t')[1:]]), score)]
                else:
                    uid_2_pid[uid] += [
                        (pid, ' '.join([text.strip() for text in CAR_data[CAR_dict[doc_id]].split('\t')[1:]]), score)]
            else:
                pass

    return None

def create_uid_2_query(args):
    resolved_queries = open(args.input_dir + "raw_utterance_allennlp_tell_me", 'r', encoding='utf-8').readlines()
    uid_2_query = {}  # uid -> query
    for line in resolved_queries:
        uid, query = line.strip().split('\t')
        uid_2_query[uid.strip()] = query.strip()

    return uid_2_query

def format_2_json(args,uid_2_pid, uid_2_query):
    uid_2_JSON = {}  # Dictionary to store json prep file

    for uid, data in uid_2_pid.items():
        for (pid, passage, score) in data:
            if int(score) >= int(args.score_threshold):
                if uid not in uid_2_JSON:  # Why would the uid not have any hard negatives...
                    if uid not in uid_2_query:
                        print("Query {} with positive passage doesn't have a query".format(uid))
                        continue

                    uid_2_JSON[uid] = {'question': uid_2_query[uid],
                                       "answers": [""],
                                       "positive_ctxs": [{"title": "",
                                                          "text": passage.strip(),
                                                          "score": int(score.strip()),
                                                          "title_score": int(0),
                                                          "passage_id": str(pid.strip())
                                                          }],
                                       "negative_ctxs": [""],  # Leave empty since we in-batch sample
                                       "hard_negative_ctxs": [""]}
                else:  # Already this qid in dictionary
                    uid_2_JSON[uid]["positive_ctxs"] += [{"title": "",
                                                          "text": passage.strip(),
                                                          "score": int(score.strip()),
                                                          "title_score": int(0),
                                                          "passage_id": str(pid.strip())
                                                          }]

    return uid_2_JSON

def create_json(args,pre_json_data):
    '''
    Output JSON file to selected directory
    :param pre_json_data:
    :return:
    '''
    filename = 'TREC_CAsT' + '.json'  # Grab train|dev|eval
    placeholder_out = ""  # REPLACE WITH ARGS
    with open(args.output_dir + filename, 'w') as json_file:
        json.dump(list(pre_json_data.values()), json_file)

    json_file.close()

    return None

def main():
    parser = argparse.ArgumentParser()

    # Before running this script run your wget and tar xzf/xf
    # To ensure all needed file are within reach of this script
    # input_dir -> MARCO collection, CAR collection, raw_utterance_allennlp_tell_me, train_topics_mod.qrel
    # output_dir -> final json file
    # car_collection dir -> partitions of CAR collection (x8)

    # Grab output directory from user
    parser.add_argument("--output_dir", default="", type=str,
                        help="Name of output location")

    # Grab location of input data
    parser.add_argument("--input_dir", default="", type=str,
                        help="Set to where all data files will be stored")

    # Grab location for car collection and where partitions will be written to
    parser.add_argument("--ctx_files_dir", default="", type=str,
                        help="Location for storing CAR and MSMARCO collection which will be used as ctx_file")

    # Set score threshold for what is considered a pos ctx
    parser.add_argument("--score_threshold", default=2, type=int,
                        help="Location for storing CAR collection")

    args = parser.parse_args() # Make them reachable

    # Create deduplicate dict for MARCO and marco pid -> passage dict from deduplicate marco subset
    dup_dict = create_dup_dict(args)
    marco_p2p = create_pid_2_pass(args, dup_dict) # MARCO ~2.9 GB should fit in memory..

    # Partition the CAR collection
    partition_CAR(args)  # Create splits of CAR_collection_X

    # {uid:[(pid, passage, score),...]} # actual text of query append later
    uid_2_pid = {}

    # Create lists linking pos passages from each dataset to respective uid
    # So we can link separately to minimize # of reads.
    marco_scored, car_scored = seperate_qrel(args)
    search_marco_qrel(marco_scored, marco_p2p, uid_2_pid)
    search_car_qrel(args, car_scored, uid_2_pid)
    # marco_p2p, marco_scored, car_scored now ties up useless memory

    # Last steps to re-format and create json files
    uid_2_query = create_uid_2_query(args)
    pre_json_data = format_2_json(args,uid_2_pid, uid_2_query)
    create_json(args, pre_json_data)

    # CAR collection written to a folder already
    # Need to write MSMARCO collection as well

if __name__ == "__main__":
    main()