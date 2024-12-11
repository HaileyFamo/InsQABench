from langchain_community.utilities import SQLDatabase
import json
import re

def get_table_info():
    table_info = '''
    CREATE TABLE `保险公司` (
    	`公司编号` INTEGER UNSIGNED NOT NULL AUTO_INCREMENT, 
    	`法定名称` VARCHAR(255), 
    	`成立时间` VARCHAR(255), 
    	`法定代表人` VARCHAR(255), 
    	`官方网址` VARCHAR(255), 
    	`公司住所` VARCHAR(255), 
    	`注册资本(亿元人民币)` FLOAT(10, 2), 
    	`经营范围` VARCHAR(255), 
    	`公司缩写` VARCHAR(255), 
    	`公司类型` VARCHAR(20), 
    	`所属公司编号` INTEGER, 
    	`公司总机` VARCHAR(20), 
    	`经营区域` VARCHAR(240), 
    	`客服热线` VARCHAR(20), 
    	`传真` VARCHAR(28), 
    	`邮编` VARCHAR(8), 
    	`营业场所` VARCHAR(255), 
    	PRIMARY KEY (`公司编号`)
    )
    CREATE TABLE `保险产品` (
    	`产品编号` INTEGER NOT NULL AUTO_INCREMENT, 
    	`产品名称` VARCHAR(255) NOT NULL, 
    	`产品类型` VARCHAR(255), 
    	`特色` VARCHAR(1100), 
    	`适宜人群` VARCHAR(255), 
    	`产品网址` VARCHAR(200), 
    	`责任免除` VARCHAR(2100), 
    	`免赔金额（元人民币）` VARCHAR(500), 
    	`保险期间` VARCHAR(1000), 
    	`等待期` VARCHAR(1000), 
    	`犹豫期` VARCHAR(1200), 
    	`保险责任` VARCHAR(2600), 
    	`交费方式/投保年龄` VARCHAR(1000), 
    	`公司编号` INTEGER UNSIGNED, 
    	`销售状态` VARCHAR(8), 
    	`红利` VARCHAR(2000), 
    	`保单贷款` VARCHAR(2400), 
    	PRIMARY KEY (`产品编号`), 
    	CONSTRAINT cp FOREIGN KEY(`公司编号`) REFERENCES `保险公司` (`公司编号`)
    )'''
    return table_info


def get_thought(text):
    try:
        thought_match = re.search(r'#Thought#:(.*?)(?=\n<sql>|<sql>)', text, re.DOTALL)
        if thought_match:
            last_thought = thought_match.group(1).strip()  # 去除首尾的空白字符
            return last_thought
        else:
            return 'err'
    except Exception as e:
        return f'err{e}'


def get_sql(text):
    try:
        # sql_match = re.search(r'#SQL#:(.*)', text)
        sql_match = re.search(r'<sql>(.*?)(?=</sql>)', text, re.DOTALL)
        sql_match2 = re.search(r'```sql(.*?)(?=#|```|$)', text, re.DOTALL)
        sql_match3 = re.search(r'<(.*?)(?=>|$)', text, re.DOTALL)
        # print(f'sql_match:{sql_match.group(1).strip()}')
        if sql_match or sql_match2 or sql_match3:
            if sql_match3:
                last_sql = sql_match3.group(1).strip()  # 去除首尾的空白字符
            elif sql_match2:
                last_sql = sql_match2.group(1).strip()  # 去除首尾的空白字符
            else:
                last_sql = sql_match.group(1).strip()  # 去除首尾的空白字符
            return last_sql
        else:
            return 'err'
    except Exception as e:
        return f'err{e}'


def get_eval_data():
    with open('delete.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data


def get_db_link():
    db = SQLDatabase.from_uri(f"mysql+pymysql://root:20020612fk@localhost/insurance",
                              sample_rows_in_table_info=0)

    return db


def run_sql(dbs, sql):
    try:
        results = dbs.run(sql)
        return f'{results}'
    except Exception as e:
        return f'err:{e}'

def changesql(sql):
    if 'LIMIT' not in sql:
        if sql.startswith(';'):
            sql = sql.replace(';',' LIMIT 8')
        else:
            sql += "LIMIT 8"
    return sql


def write2json(new_ins, json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        js = json.load(f)
        data = js
        data.append(new_ins)

    with open(json_path, 'w', encoding='utf-8') as wf:
        wf.write(json.dumps(js, indent=4, ensure_ascii=False))


if __name__ == '__main__':
    db = get_db_link()
    res = db.run("SELECT `产品名称` FROM `保险产品` LIMIT 3;")
    print(res)

