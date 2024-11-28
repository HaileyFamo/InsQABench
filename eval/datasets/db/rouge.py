import json
import os

from rouge_chinese import Rouge
import jieba  # you can use any other word cutting library


def rouge_score(generated_text, reference_texts):

    generated_text = ' '.join(jieba.cut(generated_text))

    reference_texts = ' '.join(jieba.cut(reference_texts))

    rouge = Rouge()
    scores = rouge.get_scores(generated_text, reference_texts)
    rouge_1 = scores[0]['rouge-1']['f']
    rouge_2 = scores[0]['rouge-2']['f']
    rouge_3 = scores[0]['rouge-l']['f']
    return rouge_1, rouge_2, rouge_3

def eval(path):
    with open("test.json", 'r', encoding='utf-8') as f:
        standarad_data = json.load(f)

    with open(f"data/{path}", 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(len(data))
    bleu_score_list = []
    for i in range(1,101):
        item = {}
        item['ID'] = i
        print(i)
        a1,a2,al = rouge_score(f":{data[i-1]['Answer']}",standarad_data[i-1]['Answer'])

        item['rouge-1'] = a1
        item['rouge-2'] = a2
        item['rouge-l'] = al
        bleu_score_list.append(item)

    os.makedirs(os.path.dirname(f"rouge/{path}"), exist_ok=True)
    with open(f"rouge/{path}", 'w', encoding='utf-8') as wf:
        wf.write(json.dumps(bleu_score_list, indent=4, ensure_ascii=False))

if __name__ == '__main__':
    eval('qw-lora-merge.json')
