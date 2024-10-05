# 端到端问答
import ast
import copy
import os
import json
import pdb
import difflib
import re
import prompt as prompt
from openai import OpenAI
# import google.generativeai as genai


client = OpenAI(
    base_url='https://api.openai-proxy.org/v1',
    api_key=os.environ.get(['OPENAI_API_KEY']),
)


def load_json(input_dir, output_path):
    result = {}
    for filename in os.listdir(input_dir):
        if filename.endswith('.json'):
            model_name = filename[:-5]
            
            with open(os.path.join(input_dir, filename), 'r') as f:
                data = json.load(f)
            
            for item in data:
                name = item['name']
                question = item['question']
                answer = item['answer']
                
                if name not in result:
                    result[name] = {}
                
                if question not in result[name]:
                    result[name][question] = {}
                
                result[name][question][model_name] = answer
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


def combine_json(input_dir, output_path):
    # 将各个模型的回答合并到一个json文件中
    result = {}
    for filename in os.listdir(input_dir):
        if filename.endswith('.json'):
            model_name = filename[:-5]
            
            with open(os.path.join(input_dir, filename), 'r') as f:
                data = json.load(f)
            
            for item in data:
                name = item['name'].strip()
                question = item['question'].strip()
                answer = item['answer'].strip()
                
                close_matches = difflib.get_close_matches(name, result.keys(), n=1, cutoff=0.8)
                if close_matches:
                    name = close_matches[0]
                else:
                    result[name] = {}
                
                close_matches = difflib.get_close_matches(question, result[name].keys(), n=1, cutoff=0.8)
                if close_matches:
                    question = close_matches[0]
                else:
                    result[name][question] = {}
                
                result[name][question][model_name] = answer
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


def load_and_ask_new(eval_path, output_path):
    cnt = 0

    with open(eval_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    model_scores = {'model 1': [], 'model 2': [], 'model 3': [], 'model 4': [], 'model 5': [], 'model 6': [], 'model 7': []}

    for name, questions in data.items():
        for question, answers in questions.items():
            new_answers = {}
            text = ""
            new_answers['model 1'] = answers['gpt4']
            new_answers['model 2'] = answers['kimi'] 
            new_answers['model 3'] = answers['chatpdf']
            new_answers['model 4'] = answers['qwen']
            new_answers['model 5'] = answers['yiyan']  
            new_answers['model 6'] = answers['Qwen']
            new_answers['model 7'] = answers['InsLLM']

            for model, answer in new_answers.items():
                text += f'{model}:{answer}\n'
            prompt_text = prompt.get_eval_pmt(question, answers['p'], answers['answer'], text)

            while True:
                try:
                    response = ask_gpt(prompt_text)
                    scores = extract_scores_check(response)
                    if scores is not None:
                        break
                except Exception as e:
                    print(f"Error occurred: {e}. Retrying...")
            for model in model_scores.keys():
                model_scores[model].append(scores[model])
            result = {'name': name, 'question': question, 'para': answers['p'], 'response': response, 'scores': scores}
            # pdb.set_trace()
            avg_scores = {model: {key: sum(d[key] for d in model_scores[model])/len(model_scores[model]) for key in model_scores[model][0]} for model in model_scores.keys()}
            if cnt % 10 == 0:
                print(avg_scores)
                pdb.set_trace()
            with open(output_path, 'a', encoding='utf-8') as wf:
                json_obj = json.dumps(result,ensure_ascii=False)
                wf.write(json_obj+'\n')
            cnt += 1

    avg_scores = {model: {key: sum(d[key] for d in model_scores[model])/len(model_scores[model]) for key in model_scores[model][0]} for model in model_scores.keys()}
    print(avg_scores)
            

def check_answers(input_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    for name, questions in data.items():
        for question, answers in questions.items():
            if len(answers) != 9:
                pdb.set_trace()
                print(f"问题 '{question}' 在 '{name}' 中的回答数量不是6，而是 {len(answers)}")
            if 'Qwen' not in answers or 'InsLLM' not in answers:
                pdb.set_trace()
                print(f"问题 '{question}' 在 '{name}' 中没有 Qwen 或 InsLLM 的回答")


def extract_scores_check(reply):
    pattern = re.compile(r"```json\n(.+)\n```", re.DOTALL)

    try:
        scores = ast.literal_eval(reply)
        scores = {standard.lower(): score for standard, score in scores.items()}
        for model in ['model 1', 'model 2', 'model 3', 'model 4', 'model 5', 'model 6', 'model 7']:
            assert scores[model], "Invalid scores."
            assert 'accuracy' in scores[model] and 'completeness' in scores[model] and 'clarity' in scores[model], "Invalid keys in scores."
        print("Extract succeed!")
        return scores
    except:
        match = re.search(pattern, reply)
        if match is not None:
            scores = ast.literal_eval(match.group(1))
            scores = {standard.lower(): score for standard, score in scores.items()}
            if scores:
                for model in ['model 1', 'model 2', 'model 3', 'model 4', 'model 5', 'model 6', 'model 7']:
                    assert scores[model], "Invalid scores."
                    assert 'accuracy' in scores[model] and 'completeness' in scores[model] and 'clarity' in scores[model], "Invalid keys in scores."
                print("Extract succeed!")
                return scores
        else:
            print("No match found.")
            print(f"Invalid text:{reply}")
            return None


def ask_gpt(text, model="gpt-4-turbo-preview"):
    chat = client.chat.completions.create(
    messages=[
        {
            "role": "user", 
            "content": [{'type':'text', 'text':text}]
        }
    ],
    model=model,
    # stream=True
    )
    return chat.choices[0].message.content


if __name__ == '__main__':
    import os
    if not os.path.exists('../result'):
        os.makedirs('../result')
    load_and_ask_new('../result/answers.json', '../response/answers_with_rate.jsonl')
    