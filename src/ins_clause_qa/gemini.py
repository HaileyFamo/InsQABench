# -*- coding: utf-8 -*-

import json
import os
import random
import time
from InsQABench.src.ins_clause_qa.train_prompt import pmt1, pmt2, pmt3
from utils import *
from config import *



def save_qae_new(jsonl_dir, qa_dir, check_dir, max_waiting=120):
    pdf_name = []
    for root, _, files in os.walk(check_dir):
        for file in files:
            with open(os.path.join(root, file), 'r', encoding='utf-8') as file:
                for line in file:
                    json_obj = json.loads(line)
                    if json_obj["PDF name"] not in pdf_name:
                        pdf_name.append(json_obj["PDF name"])
    print(f"Get {len(pdf_name)} PDFs.")

    for root, dirs, files in os.walk(jsonl_dir):
        for idx, file in enumerate(files):
           
            results = []
            if not file.endswith('.json'):
                logger.warning("Found a non-json file.")
                continue
            pdf_now = os.path.basename(file).split('.')[0]
            if pdf_now in pdf_name:
                continue

            data = read_jsonl(os.path.join(jsonl_dir, file))

            long_paras = [para['内容'] for para in data if len(para['内容']) >= 100]
            if len(long_paras) == 0:
                continue
            if len(long_paras) < 20:
                paras = long_paras
            else:
                paras = random.sample(long_paras, 20)
            for para in paras:
                caption = None
                if len(para) < 200:
                    question = pmt1
                elif len(para) < 500:
                    question = pmt2
                else:
                    question = pmt3
                start_time = time.time()
                fail = 0
                attempt = 0
                while True:
                    try:
                        if attempt > 5:
                            logging("Found a para cannot generate valid question, skip.")
                            break
                        response = text_model.generate_content(question + para, stream=False)
                        response.resolve()
                        res = [part.text for part in response.candidates[0].content.parts]
                        res = res[0]
                        if res:
                            qa = extract_qa_pairs(res)
                            if qa:
                                result = {"PDF name": pdf_now, "Para text": para}
                                result["Gemini gen"] = qa
                                results.append(result)
                                break
                            else:
                                attempt += 1
                                time.sleep(5 + random.randint(10, 20))
                    except Exception as e:
                        fail += 1
                        if fail >= 5:
                            break
                        print(e)
                        time.sleep(5 + random.randint(10, 20))

                end_time = time.time()
                if end_time - start_time > max_waiting:
                    logger.warning("Exceed max waiting time.")

            if not results:
                print("No para in this PDF is processed.")

            write_jsonl(results, os.path.join(qa_dir, f'gemini_gen.jsonl'))



def save_qae_docx(jsonl_dir, qa_dir, max_waiting=120):

    exist_pdf = check_exist(qa_dir)

    for root, dirs, files in os.walk(jsonl_dir):
        for idx, file in enumerate(files):
            results = []
            if not file.endswith('.jsonl'):
                logger.warning("Found a non-jsonl file.")
                continue
            pdf_now = os.path.basename(file).split('.')[0]
            data = read_jsonl(os.path.join(jsonl_dir, file))
            long_paras = [para['text'] for para in data if len(para['text']) >= 100]

            if len(long_paras) == 0:
                continue
            if len(long_paras) < 50:
                paras = long_paras
            else:
                paras = random.sample(long_paras, 50)
            for para in paras:
                caption = None
                if len(para) < 200:
                    question = pmt1
                elif len(para) < 500:
                    question = pmt2
                else:
                    question = pmt3
                start_time = time.time()
                fail = 0
                attempt = 0
                while True:
                    try:
                        if attempt > 3:
                            print("Found a para cannot generate valid question, skip.")
                            break
                        response = text_model.generate_content(question + para, stream=False)
                        response.resolve()
                        res = [part.text for part in response.candidates[0].content.parts]
                        res = res[0]
                        if res:
                            qa = extract_qa_pairs(res)
                            if qa:
                                result = {"PDF name": pdf_now, "Para text": para}
                                result["Gemini gen"] = qa
                                results.append(result)
                                break
                            else:
                                attempt += 1
                                print(para)
                                time.sleep(30 + random.randint(10, 20))
                    except Exception as e:
                        fail += 1
                        if fail >= 5:
                            break
                        print(e)
                        time.sleep(30 + random.randint(10, 20))

                end_time = time.time()
                if end_time - start_time > max_waiting:
                    logger.warning("Exceed max waiting time.")

            if not results:
                print("No para in this PDF is processed.")

            write_jsonl(results, os.path.join(qa_dir, f'gemini_gen.jsonl'))


if __name__ == "__main__":
    pass