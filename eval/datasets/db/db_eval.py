import os
import time
import openai
import json
import ast

from openai import OpenAI
def gpt4o_ans(prompt):
    time.sleep(4)
    os.environ["MIT_SPIDER_TOKEN"] = ""
    client = OpenAI(
        base_url="http://47.88.8.18:8088/v1",
        api_key=os.environ["MIT_SPIDER_TOKEN"]
    )
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    response = completion.choices[0].message
    return response.content


API_KEY = "sk-4e9afcccc35e4cc0bb2e6b55cc64f8b2"
class DeepSeek:
    def __init__(self):
        self.client = openai.OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")

    def classify(self, prompt):
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0,
            stream=False,
        )
        return response.choices[0].message.content


def get_eval_prompt(question, standard, model_answer):
    prompt = f'''现在你需要作为一个评委，对下面几个保险领域问题的回答进行打分，我会给你用户问题Question的一个标准答案StandardAnswer。这个标准答案是正确的。
    然后给你一个待测评的回答。请你对这个待评测回答进行打分，分值在0~100之间。打分标准如下:
    (1)待评测答案与标准答案StandardAnswer的主要内容是否一致，也就是回答的要点是否都有。
    (2)待评测答案的回答是否准确与严谨，即如果搜索到的结果与用户问的实体名称不一致，是否强调了相似性，而不是直接回答。
    (3)检测是否有编造答案的行为，如果编造答案或者错答，得分应该降低。
    (4)如果漏答，则按照所答要点占标准答案的百分比来酌情给分。
    (5)如果没有查询到想要的产品，但是得到了相似的产品，可以给更高的分。


    你只需要给出这个回答的一个分数，不需要你解释为什么。
    输出格式为:
    [<Score>:"分值"]

    举个例子:
    用户问题Question:济南农民工工资保证险（多年期）属于什么类型保险？
    StandardAnswer:抱歉，我们无法找到“济南农民工工资保证险（多年期）”这款产品，但我们发现了以下相似的产品：
- 永诚山东济南农民工工资支付履约保证保险（多年期），属于履约保证保险。
- 山东济南地区农民工工资支付履约保证保险，属于履约保证保险。
- 山东省济南市农民工工资支付履约保证保险（多年期），属于工程保险。
如果您要查询的是以上产品，请告知我产品的名称，我将为您查询。
    下面是一些待评测答案，以及对应的分数:
    Answer:非常抱歉，关于济南农民工工资保证险（多年期）的具体保障范围，我们无法通过现有的数据表进行查询。为了给您提供更准确的答案，请提供一些详细信息，例如该产品的保障范围、保障期限等，以便我们为您提供更精确的解答。
    [<Score>:"8"]
    Answer:抱歉，我们没有找到济南农民工工资保证险（多年期）属于什么类型保险的信息，但是我们找到了相似的产品，如：永诚山东济南农民工工资支付履约保证保险（多年期）该产品是履约保证保险，山东省济南市农民工工资支付履约保证保险（多年期）该产品是工程保险。如果不是您想要查找的产品，请提供更准确的产品名称。
    [<Score>:"100"]
    Answer:济南农民工工资保证险（多年期）属于工程保险类型。
    [<Score>:"50"]
    Answer:对不起，经过我们的查询，我们未能找到完全匹配"济南农民工工资保证险（多年期）"的产品信息。可能是因为这个特定的组合在数据库中没有明确记录，或者描述略有差异。请确认一下产品名称是否有误，或者您可以提供更多信息以便我们更精确地帮您查找.
    [<Score>:"13"]
    Answer:抱歉，我无法找到济南农民工工资保证险（多年期）的保险类型信息。
    [<Score>:"0"]

    现在轮到你针对下面的用户问题以及标准答案来对不同的回答进行打分了:
    用户问题Question:{question}
    StandardAnswer:{standard}
    下面是待测评答案:
    Answer:{model_answer}
    请你按要求给出这个回答的分数
    '''
    return prompt


def get_data(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data

# 将新一条数据写入json文件
def write2json(new_ins, json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        js = json.load(f)
        data = js
        data.append(new_ins)

    with open(json_path, 'w', encoding='utf-8') as wf:
        wf.write(json.dumps(js, indent=4, ensure_ascii=False))


# 从回答中提取分数
def get_dict(str):
    dict_str = str.replace('<', '"').replace('>', '"')
    print(f"dict_str:{dict_str}")
    if dict_str.startswith('[') and dict_str.endswith(']'):
        dict_str = dict_str.replace('[', '{').replace(']', '}')
    else:
        dict_str = '{' + dict_str + '}'
    dict_re = ast.literal_eval(dict_str)

    return dict_re


# 找到前100个测试集中，没有用到的案例
def find_extra_elements(subarray):
    # fu = [i for i in range(1, 101)]
    fu = [2, 3, 6, 10, 14, 23, 26, 29, 33, 34, 38, 39, 42, 43, 47, 52, 56, 61, 66, 68, 69, 73, 76, 80, 82, 83, 88, 89, 91, 92, 95, 100]

    # 将数组转换为集合，以便我们可以使用集合操作
    parent_set = set(fu)
    sub_set = set(subarray)
    # 使用差集操作找出父数组中除了子数组元素之外的其他元素
    extra_elements = parent_set - sub_set
    # 将结果转换回列表，如果需要的话
    return list(extra_elements)


def eval(path):
    model = DeepSeek()

    standard_datas = get_data('test.json')  # test.json文件中的为标准答案

    ans_datas = get_data(f'data{path}')  # 不同模型的回答答案

    with open(f'goal{path}', 'r', encoding='utf-8') as f:
        zi = json.load(f)
        print(len(zi))
    haizi = []
    for i in zi:
        haizi.append(i['ID'])
    ee = find_extra_elements(haizi) ## ee中存放的是前100中，未评测的数据
    print(ee)
    for i in ee:
        try:
            question = standard_datas[i-1]['input']
            id = standard_datas[i-1]['ID']
            print(id)

            standard_answer = standard_datas[i-1]['Answer']
            for item in ans_datas:
                if item['ID'] == i:
                    model_answer = item['Answer']
                    break

            prompt = get_eval_prompt(question, standard_answer, model_answer)

            res = model.classify(prompt)

            ans_dict = get_dict(res)
            eval_dict = {}
            eval_dict['ID'] = id
            eval_dict['Question'] = question
            eval_dict['Standard'] = standard_answer
            eval_dict['ModelAnswer'] = model_answer
            eval_dict['score'] = int(ans_dict['Score'])

            write2json(eval_dict, f'./goal/{path}')
        except Exception as e:
            print(e)

if __name__ == '__main__':
    eval('/mkours.json')
