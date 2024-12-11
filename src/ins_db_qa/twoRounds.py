import database as db
import json
import re
import time
import os
from openai import OpenAI

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


def get_sql_prompt(question, table_info):
    prompt = f'''你是一个保险领域的数据库工程师,现在让你分析用户的问题input以及数据库中的表的结构信息，写出解决该问题可能用到的所有SQL语句。
    SQL语句是mysql标准，并且用<sql></sql>包裹起来，如果有多个SQL语句，请分别用多个<sql></sql>包裹起来。请确保生成的SQL语句可执行。
    你只需要回答<sql></sql>中的内容，不需要你回答其他内容，不需要你解释为什么。
    下面是你可能用到的数据库表的信息:\n{table_info}

    示例1:
    input:
    英大人寿补充团体医疗险可以保障多大岁数的人？这款产品可以保障什么样的医疗责任？
    output:
    <sql>SELECT `产品编号`,`产品名称` FROM `保险产品` WHERE `产品名称` = '英大人寿补充团体医疗险'</sql>
    <sql>SELECT `保险责任` FROM `保险产品` WHERE `产品名称` = '英大人寿补充团体医疗险'</sql>

    现在轮到你回答了:
    input:
    {question}
    output:
    '''
    return prompt


def get_answer_prompt(history):
    prompt = f'''你作为一个保险行业的客服，现在给你一个用户的问题以及从数据库中的查询结果,请你以客服的语气来回答用户提出的问题。
    其中，<sql></sql>中是需要查询的SQL语句，<exe></exe>中是对应的查询结果。
    请你根据查询结果，回答提出的问题。
    注意:
    (1)你应该注意以客服的语气来写Answer。
    (2)所有Answer的内容必须基于<exe></exe>中的内容，不能够按照自己的知识回答Question
    (3)不能回答与Question无关的问题，你只需要根据前面的内容回答用户Question的问题，不需要你分析问题，也不需要你生成SQL语句

    下面是一些例子:
    input:
    Question:华贵多彩年年年金保险属于哪种产品类型？
    <sql>SELECT `产品名称`,`产品类型` FROM `保险产品` WHERE `产品名称` LIKE '%华%贵%多%彩%年%年%年%金%保%险%'</sql>
    <exe>[('华贵多彩年年年金保险（分红型）\\n\\n', '分红保险\\n\\n')]</exe>
    output:
    抱歉，我们没有找到华贵多彩年年年金保险产品的类型信息，但是我们找到了相似的产品:华贵多彩年年年金保险（分红型）,该产品是分红保险。如果不是您想要查找的产品，请提供更准确的产品名称。

    现在轮到你回答了:
    input:
    {history}
    output:'''
    return prompt


def getSqlList(text):
    # 使用正则表达式匹配 <sql> 和 </sql> 之间的内容
    pattern = r'<sql>(.*?)</sql>'
    # 使用 re.findall 找到所有匹配的内容
    sql_list = re.findall(pattern, text, re.DOTALL)
    new_sql_list = []
    for sql in sql_list:
        sql = db.changesql(sql)
        new_sql_list.append(sql)
    return new_sql_list

def getExeList(dbs,sql_list):
    exe_list = []
    for sql in sql_list:
        sql_result = db.run_sql(dbs, sql)
        exe_list.append(sql_result)
    return exe_list

def getHistory(sql_list,exe_list):
    history =""
    for i in range(len(sql_list)):
        history += f"<sql>{sql_list[i]}</sql>\n<exe>{exe_list[i]}</exe>\n"
    return history

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

    sql_prompt = get_sql_prompt(data['Question'], table_info)
    text = gpt3p5_ans(sql_prompt)
    print(f'text:{text}')
    sql_list = getSqlList(text)
    data["sql_list"] = sql_list
    exe_list = getExeList(dbs, sql_list)
    data["exe_list"] = exe_list
    history = getHistory(sql_list, exe_list)
    answer_prompt = get_answer_prompt(history)
    answer = gpt3p5_ans(answer_prompt)
    data['answer'] = answer

    db.write2json(data, 'answers/gpt3p5-simple.json')
    print(f'{data["ID"]}写入成功！')
    return 1

if __name__ == '__main__':
    dbs = db.get_db_link()
    table_info = db.get_table_info()
    datas = db.get_eval_data()
    #
    with open('./answers/gpt3p5-simple.json', 'r', encoding='utf') as f:
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

