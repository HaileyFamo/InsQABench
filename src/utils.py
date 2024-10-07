import os
import json
import logging
import pdb
import random


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def read_jsonl(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            json_obj = json.loads(line)
            data.append(json_obj)
    return data


def write_jsonl(data, file_path):
    with open(file_path, 'a', encoding='utf-8') as file:
        for json_obj in data:
            json_string = json.dumps(json_obj, ensure_ascii=False)
            file.write(json_string + '\n')


def extract_qa_pairs(text):
    qa_dict = {}
    questions = re.split(r'\*\*\[\w+\]\*\*[：:]', text)[1:]
    for i in range(0, len(questions), 2):  # iterate over pairs of questions and answers
        q = questions[i].strip()
        a = questions[i + 1].strip() if i + 1 < len(questions) else ''  # handle case where text ends with a question
        qa_dict[f"Generated {int(i / 2) + 1}"] = {"Q": q, "A": a}

    if not qa_dict.get('Generated 1'):
        logger.warning(f"Didn't get even 1 qa:{qa_dict}")
        logger.warning(text)
        return None
    # print(qa_dict)
    return qa_dict


def check_exist(indir):
    pdfs = []
    for root, dirs, files in os.walk(indir):
        for file in files:
            if file.endswith('.jsonl'):
                data = read_jsonl(os.path.join(indir, file))
                for para in data:
                    if para['PDF name'] not in pdfs:
                        pdfs.append(para['PDF name'])
    return pdfs


def count_json(file):
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(len(data))

def split(input_file, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    pdb.set_trace()
    random.shuffle(data)
    train_data = data[:int(len(data) * 0.9)]
    test_data = data[int(len(data) * 0.9):]
    print(len(train_data), len(test_data))
    with open(os.path.join(output_dir, 'train.json'), 'w', encoding='utf-8') as f:
        json.dump(train_data, f, ensure_ascii=False)
    with open(os.path.join(output_dir, 'test.json'), 'w', encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False)


if __name__ == '__main__':
    split('/data/linbinbin/InsLLM/LLaMA-Factory/data/final.json', '/data/linbinbin/InsLLM/LLaMA-Factory/data0905')
 