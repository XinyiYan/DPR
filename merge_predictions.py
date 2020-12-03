import json
import glob
import argparse


def merge_predictions(files, output_file, pred_num=1000):
    merged_data = {}
    id_2_q = {}
    for _, path in enumerate(files):
        flag = True
        with open(path, 'r', encoding="utf-8") as f:
            print('Reading file %s' % path)
            data = json.load(f)
            for item in data:
                question = item['question']
                q_id = item['question_id']
                ctxs = item['ctxs']
                if flag:
                    print(path, 'num of ctxs', len(ctxs))
                    flag = False
                if q_id not in merged_data:
                    merged_data[q_id] = ctxs
                else:
                    merged_data[q_id].extend(ctxs)
                id_2_q[q_id] = question

    to_json = []
    for qid in merged_data:
        ctxs = sorted(merged_data[qid], reverse=True,
                      key=lambda x: x['score'])[:pred_num]
        to_json.append({
            "question_id": qid,
            "question": id_2_q[qid],
            "answers": "not available",
            "ctxs": ctxs
        })

    with open(output_file, 'w') as jsonfile:
        json.dump(to_json, jsonfile, indent=4)

    print('num of questions', len(id_2_q))
    print(to_json[0]["question"], len(to_json[0]["ctxs"]))
    print('num of merged data', len(merged_data))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--files", default="", type=str,
                        help="Glob path to the files to be merged")
    parser.add_argument("--output", default="", type=str, help="output file")
    parser.add_argument("--topk", default=1000, type=int,
                        help="keep the top k results")
    args = parser.parse_args()

    files_pattern = args.files
    files_path = glob.glob(files_pattern)
    print(files_path)

    merge_predictions(files_path, args.output, args.topk)


if __name__ == "__main__":
    main()
