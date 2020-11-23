import argparse
import json

def create_pid_2_qid(args):
    '''
    Function to create dict of pid-> [qid,...]. Add passage on pid.
    :param args:
    :return:
    '''

    pid_2_qid = {}  # dict for linking positive passage from collection to qrel pid

    with open(args.input_dir + args.qrel_filename) as infile:
        for line in infile:
            qid, _, pid, rel = line.split('\t')
            if pid not in pid_2_qid:
                pid_2_qid[pid] = [qid]
            else:  # multiple pids serve diff question
                pid_2_qid[pid] += [qid]
    infile.close()

    with open(args.input_dir + "collection.tsv") as infile:
        for line in infile:
            pid, passage = line.split('\t')
            if pid in pid_2_qid:
                pid_2_qid[pid] += [passage.rstrip()]  # [qid_1, ..., qid_n, passage]
            else:
                continue
    infile.close()


    return pid_2_qid

def create_qid_2_query(args):
    '''
    Create dictionary for qid -> query.
    This needed since we aren't using hard negatives yet.
    Otherwise get query from there^.
    :param args:
    :return:
    '''
    qid_2_query = {} #{qid:QUERY}
    with open(args.input_dir + args.query_filename) as infile:
        for line in infile:
            qid, query = line.split('\t')
            if qid not in qid_2_query:
                qid_2_query[qid] = query.rstrip()
            else:
                print('Error: There is a duplicate qid being adding to qid_2_query.')
    infile.close()

    return qid_2_query

def format_2_json(pid_2_qid, qid_2_query):
    '''
    :param pid_2_qid:
    :return:
    '''
    qid_2_JSON = {}  # Dictionary to store json prep file

    for pid, data in pid_2_qid.items():
        passage = data[-1]
        for qid in data[:-1]:
            if qid not in qid_2_JSON:  # Why would the qid not have any hard negatives...
                if qid not in qid_2_query:
                    print("Query {} with positive passage doesn't have a query".format(qid))
                    continue

                qid_2_JSON[qid] = {'question':qid_2_query[qid],
                                   "answers":[""],
                                   "positive_ctxs":[{"title":"",
                                                      "text": passage,
                                                      "score":1,
                                                      "title_score":int(0),
                                                      "passage_id":str(pid)
                                                      }],
                                   "negative_ctxs":[""],  # Leave empty since we in-batch sample
                                   "hard_negative_ctxs":[""]}
            else: # Already this qid in dictionary
                qid_2_JSON[qid]["positive_ctxs"] += [{"title": "",
                                                      "text": passage,
                                                      "score": 1,
                                                      "title_score": int(0),
                                                      "passage_id": str(pid)
                                                      }]

    return qid_2_JSON

def create_json(args, pre_json_data):
    '''
    Output JSON file to selected directory
    :param pre_json_data:
    :return:
    '''
    # MSMARCO.(train|dev|eval).json <- output file format.
    filename = 'MSMARCO' + '.' + args.query_filename.split('.')[1] + '.json' # Grab train|dev|eval

    with open(args.output_dir + filename, 'w') as json_file:
        json.dump(list(pre_json_data.values()), json_file)

    json_file.close()

    return None

def main():
    parser = argparse.ArgumentParser()

    # Before running this script run your wget and tar xzf
    # To ensure all needed file are within reach of this script

    # Grab output directory from user
    parser.add_argument("--output_dir", default="", type=str,
                        help="Name of output location")

    # Grab location of input data
    parser.add_argument("--input_dir", default="", type=str,
                        help="Set to file path of where qrel and collection are located")

    # Grab location of input data
    parser.add_argument("--qrel_filename", default="", type=str,
                        help="Set to name of qrel file to be used")

    # Grab location of input data
    parser.add_argument("--query_filename", default="", type=str,
                        help="Set to name of query file to be used")


    args = parser.parse_args() # Make them reachable
    pid_2_qid = create_pid_2_qid(args)
    qid_2_query = create_qid_2_query(args)
    pre_json_data = format_2_json(pid_2_qid, qid_2_query)
    create_json(args, pre_json_data)

if __name__ == "__main__":
    main()