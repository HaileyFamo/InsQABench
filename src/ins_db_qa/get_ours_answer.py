import json
import database as db
import pandas as pd
from transformers import AutoTokenizer, AutoModelForCausalLM
import re
import time

import os
device = "cuda"
os.environ['CUDA_VISIBLE_DEVICES'] = '0,1,2'
thought_prompt = """
你是一个保险领域的数据库分析工程师，下面是数据库中的信息，请你根据数据库表的信息,分析用户的问题,得到SQL语句，并根据查询到的结果回答用户问题。\n数据库中表的信息如下:\nCREATE TABLE \"保险公司\" (\n  \"公司编号\" INTEGER NOT NULL,\n  \"法定名称\" TEXT(255),\n  \"成立时间\" TEXT(255),\n  \"法定代表人\" TEXT(255),\n  \"官方网址\" TEXT(255),\n  \"公司住所\" TEXT(255),\n  \"注册资本(亿元人民币)\" REAL,\n  \"经营范围\" TEXT(255),\n  \"公司缩写\" TEXT(255),\n  \"公司类型\" TEXT(20),\n  \"所属公司编号\" INTEGER,\n  \"公司总机\" TEXT(20),\n  \"经营区域\" TEXT(240),\n  \"客服热线\" TEXT(20),\n  \"传真\" TEXT(28),\n  \"邮编\" TEXT(8),\n  \"营业场所\" TEXT(255),\n  PRIMARY KEY (\"公司编号\")\n),\nCREATE TABLE \"保险产品\" (\n  \"产品编号\" INTEGER NOT NULL,\n  \"产品名称\" TEXT(255),\n  \"产品类型\" TEXT(255),\n  \"特色\" TEXT(1100),\n  \"适宜人群\" TEXT(255),\n  \"产品网址\" TEXT(200),\n  \"责任免除\" TEXT(2100),\n  \"免赔金额（元人民币）\" TEXT(500),\n  \"保险期间\" TEXT(1000),\n  \"等待期\" TEXT(1000),\n  \"犹豫期\" TEXT(1200),\n  \"保险责任\" TEXT(2600),\n  \"交费方式/投保年龄\" TEXT(1000),\n  \"公司编号\" INTEGER,\n  \"销售状态\" TEXT(8),\n  \"红利\" TEXT(2000),\n  \"保单贷款\" TEXT(2400),\n  PRIMARY KEY (\"产品编号\"),\n  CONSTRAINT \"wai\" FOREIGN KEY (\"公司编号\") REFERENCES \"保险公司\" (\"公司编号\")\n)
"""
ans_prompt = """

"""

def get_model():
    tokenizer = AutoTokenizer.from_pretrained("/root/autodl-tmp/Qwen1.5-14B-Chat-LoRA-check")
    model = AutoModelForCausalLM.from_pretrained("/root/autodl-tmp/Qwen1.5-14B-Chat-LoRA-check",torch_dtype="auto",device_map="auto")
    return model,tokenizer

# 模型调用逻辑
def predict(model,tokenizer,messages):
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(device)

    generated_ids = model.generate(
        model_inputs.input_ids,
        max_new_tokens=512
    )
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]

    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return response


def get_thought_sql(response):

    thoughts = re.findall(r'<Thought>(.*?)</Thought>', response, re.DOTALL)
    sql = re.findall(r'<sql>(.*?)</sql>', response, re.DOTALL)

    if len(thoughts) == 0 or len(sql) == 0:
        return 0,0
    else:
        return thoughts[0],sql[0]





def get_response_from_model(model,tokenizer,messages):

    response = predict(model, tokenizer,messages)
    return response

def react(sor,dbs,model,tokenizer):
    data = {}
    data['ID'] = sor['ID']
    data['Question'] = sor['input']
    messages = []
    messages.append({"role": "system", "content": thought_prompt})
    messages.append({"role": "user", "content": data['Question']})
    text = get_response_from_model(model,tokenizer,messages)

    count = 5
    data['Thought'] = ''

    while '<Answer>' not in text:
        print(text)
        if count == 0:
            break
        count -= 1
        print(count)
        thought,sql = get_thought_sql(text)
        if thought == 0 or sql == 0:
            return 0
        sql = db.changesql(sql)

        sql_result = db.run_sql(dbs, sql)
        messages.append({"role": "assistant", "content": f"<Thought>{thought}</Thought><sql>{sql}</sql>"})
        messages.append({"role": "user", "content": f"下面是数据库的返回结果:<exe>{sql_result}</exe>"})

        text = get_response_from_model(model, tokenizer, messages)
    data['messages'] = messages
    if '<Answer>' in text:
        answer = re.findall(r'<Answer>(.*?)</Answer>', text, re.DOTALL)
    else:
        messages[-1]['content'] += ",现在你应该直接生成回答，不需要生成thought和sql，回答的答案用<Answer></Answer>包裹"
        answer = get_response_from_model(model, tokenizer, messages)

    data['Answer'] = answer

    db.write2json(data, 'ours.json')
    print(f'{data["ID"]}写入成功！')
    return 1

def find_extra_elements(parent_array, subarray):
    # 将数组转换为集合，以便我们可以使用集合操作
    parent_set = set(parent_array)
    sub_set = set(subarray)
    # 使用差集操作找出父数组中除了子数组元素之外的其他元素
    extra_elements = parent_set - sub_set
    # 将结果转换回列表，如果需要的话
    return list(extra_elements)



if __name__ == '__main__':
    model,tokenizer = get_model()
    dbs = db.get_db_link()
    table_info = db.get_table_info()
    datas = db.get_eval_data()

    with open('ours.json', 'r', encoding='utf') as f:
        data = json.load(f)
        shuzi = []
        for item in data:
            shuzi.append(item['ID'])
        print(shuzi)
        print(len(shuzi))
        fu = [i for i in range(1, 101)]
        print(fu)
        chaji = find_extra_elements(fu, shuzi)
        print(chaji)
        print(len(chaji))
        for i in chaji:
            react(datas[i - 1],  dbs,model,tokenizer)