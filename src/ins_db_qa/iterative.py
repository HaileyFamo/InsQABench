import json
import re

import torch
from modelscope import snapshot_download, AutoModelForCausalLM
from modelscope import AutoModel,AutoTokenizer,GenerationConfig
import database as db
import time
from openai import OpenAI
import os

def gpt3p5_ans(prompt):

    os.environ["MIT_SPIDER_TOKEN"] = "your_api_key"
    client = OpenAI(
        base_url="http://47.88.8.18:8088/v1",
        api_key=os.environ["MIT_SPIDER_TOKEN"]
    )
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    response = completion.choices[0].message
    return response.content


def get_thought_prompt(history, table_info):
    prompt = f'''你是一个保险领域的数据库工程师,现在让你分析用户的问题Question，得到思考过程Thought，并写出解决该问题的SQL语句。
    我会给你数据库中表的信息和你之前的回答历史。回答历史包括之前的Thought过程、该Thought过程生成的SQL语句、以及利用该SQL语句
    从数据库中查询到的结果SQLResult。
    注意:
    (1)你需要判断，前面的查询结果是否能够回答用户的问题。如果前面的查询结果不能得到相关的信息，那么你不能轻易回答没有答案，而需要继续执行Thought过程，
    想尽办法修改之前的SQL语句（比如采用模糊匹配等方式）使SQL查询尽可能地从数据库中找到答案。如果前面得到的结果足以回答Question中的问题，那么你不需要
    进行Thought过程，直接回答"Ready!",不需要你解释为什么。
    (2)请不要很快回答Ready，确保你在回答Ready之前进行了充分的思考Thought和SQL语句的生成过程。
    (3)你不要一步就完成整个问题的SQL语句，你应该分析当前的问题，一步一步解决，并思考下一步的SQL语句应该如何编写。这个SQL语句可以是解决中间问题的一个步骤。
    我期待一个充分的思考过程和SQL语句。
    (4)生成的SQL语句为Mysql标准，一次只能生成一个SQL语句，且应该写在一行中，不需要你解释。
    (5)SQL语句用<sql></sql>包裹，执行结果用<exe></exe>包裹

    下面是你可能用到的数据库表的信息:\n{table_info}
    示例1:
    输入:
    Question:英大人寿补充团体医疗险可以保障多大岁数的人？这款产品可以保障什么样的医疗责任？
    Thought:根据question中的问题，需要查询英大人寿补充团体医疗险可以保障多大岁数的人以及这款产品可以保障什么样的医疗责任，此问题涉及到'保险产品表'中'产品名称','产品编号','保险责任'字段，首先我们应该找到英大人寿补充团体医疗险的'产品编号'，这涉及到'保险产品表'中'产品名称','产品编号'字段，写如下SQL
    <sql>SELECT `产品编号`,`产品名称` FROM `保险产品` WHERE `产品名称` = '英大人寿补充团体医疗险' </sql>
    <exe>:[]</exe>
    输出:
    Thought:上一步查找的结果为空值，不一定是数据库中的没有该数据，可能是'英大人寿补充团体医疗险'这个是产品的缩写，所以采用模糊匹配的方法，修改上面的
    <sql>SELECT `产品编号`,`产品名称` FROM `保险产品` WHERE `产品名称` LIKE '%英%大%人%寿%补%充%团%体%医%疗%险%'</sql>

    示例2:
    输入:
    Question:在保险责任里包含住院医疗保险金的保险产品有哪些？
    Thought:根据question中的问题，需要查询长城附加安心住院定额给付医疗保险的免赔天数，此问题涉及到'保险产品表'中'产品名称','免赔金额（元人民币）'字段，写如下
    <sql>SELECT `产品名称`,`免赔金额（元人民币）` FROM `保险产品` WHERE `产品名称` = '长城附加安心住院定额给付医疗保险'</sql>
    <exe>:[('长城附加安心住院定额给付医疗保险', '3天')]</exe>
    输出:
    Ready!

    现在轮到你回答了:
    输入:
    {history}
    输出:
    '''
    return prompt


def get_answer_prompt(history):
    prompt = f'''你作为一个保险行业的客服，现在给你一个用户的问题以及从数据库中的查询过程,请你以客服的语气来回答用户提出的问题。
    其中，Thought是对问题的一步步思考过程，SQL是根据这个思考决定要执行的SQL语句，SQLResult是从数据库中执行上一行的SQL语句得到的查询结果。
    请你根据这一系列的思考与查询结果，回答提出的问题。不能回答与Question无关的问题。
    注意:
    (1)你应该注意以客服的语气来写Answer。
    (2)所有Answer的内容必须基于SQLResult后面的内容，不能够按照自己的知识回答Question
    (3)Answer应该准确与严谨。比如，在查询过程中使用了模糊匹配，使查找到的结果可能与需要查询的产品名称不完全一样，这时候就不能简答的认为找到的答案就是用户想要的答案，
    你应该首先告诉用户我们没有找到完全一样的产品名称，但我们找到了下面几个相似的产品，接着回答后续的问题。如果使用了模糊匹配之后，查询到的结果中存在与用户Question中的
    实体名称完全一致的内容，就可以直接给出答复，不需要说明相似产品。不要完全按照上面的内容来回答，只需要表达准确相应的意思即可。

    下面是一个例子:
    输入:
    Question:华贵多彩年年年金保险属于哪种产品类型？
    Thought:根据question中的问题，需要查询'华贵多彩年年年金保险（分红型）'属于哪种产品类型，此问题涉及到'保险产品'表中'产品名称','产品类型'字段，写如下
    <sql>SELECT `产品名称`,`产品类型` FROM `保险产品` WHERE `产品名称` = '华贵多彩年年年金保险'</sql>
    <exe>[]</exe>
    #Thought#:上一步查找的结果为空值，不一定是数据库中的没有该数据，可能是'华贵多彩年年年金保险（分红型）'这个是产品的缩写，所以采用模糊匹配的方法，修改上面的
    <sql>SELECT `产品名称`,`产品类型` FROM `保险产品` WHERE `产品名称` LIKE '%华%贵%多%彩%年%年%年%金%保%险%'</sql>
    <exe>[('华贵多彩年年年金保险（分红型）\\n\\n', '分红保险\\n\\n')]</exe>
    输出:
    Answer:抱歉，我们没有找到华贵多彩年年年金保险产品的类型信息，但是我们找到了相似的产品:华贵多彩年年年金保险（分红型）,该产品是分红保险。如果不是您想要查找的产品，请提供更准确的产品名称。

    现在轮到你回答了:
    输入:
    {history}
    输出:
    Answer:'''

    return prompt



def find_extra_elements(parent_array, subarray):
    # 将数组转换为集合，以便我们可以使用集合操作
    parent_set = set(parent_array)
    sub_set = set(subarray)
    # 使用差集操作找出父数组中除了子数组元素之外的其他元素
    extra_elements = parent_set - sub_set
    # 将结果转换回列表，如果需要的话
    return list(extra_elements)


def react(sor, table_info, dbs):
    data = {}
    data['ID'] = sor['ID']
    data['Question'] = sor['input']
    temp = f"Question:{sor['input']}"
    thought_prompt = get_thought_prompt(temp, table_info)
    text = gpt3p5_ans(thought_prompt)
    print(f'text:{text}')
    count = 6
    data['Thought'] = ''
    while 'Ready' not in text:
        if count == 0:
            break
        count -= 1
        print(count)
        thought = db.get_thought(text)
        print(f"before_thought:{thought}")

        sql = db.get_sql(text)
        print(f"before_sql:{sql}")
        sql = db.changesql(sql)
        # sql = db.insert(sql)
        print(f'sql:{sql}')
        sql_result = db.run_sql(dbs, sql)
        print(f'sql_result: {sql_result}')
        temp = f'{temp}\nThought:{thought}\n<sql>{sql}\n</sql><exe>{sql_result}</exe>'
        data['Thought'] = f"{data['Thought']}\nThought:{thought}\n<sql>{sql}</sql>\n<exe>{sql_result}</exe>"
        thought_prompt = get_thought_prompt(temp, table_info)
        text = gpt3p5_ans(thought_prompt)
        print(f'text_inner:{text}')

    ans_prm=get_answer_prompt(temp)
    answer = gpt3p5_ans(ans_prm)
    if answer == 0:
        return 0
    data['Answer'] = answer
    db.write2json(data, 'answers/gpt3p5.json')
    print(f'{data["ID"]}写入成功！')
    return 1

if __name__ == '__main__':
    dbs = db.get_db_link()
    table_info = db.get_table_info()
    datas = db.get_eval_data()

    with open('./answers/gpt3p5.json', 'r', encoding='utf') as f:
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
            time.sleep(3)
            react(datas[i - 1], table_info, dbs)