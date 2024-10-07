import json

# 读取原始JSON文件
input_file_path = r'C:\Users\31823\Documents\CodeFolder\Python\InsQABench\eval\subjective\result\answers.json'
output_file_path = r'C:\Users\31823\Documents\CodeFolder\Python\InsQABench\eval\subjective\result\data.json'

with open(input_file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# 准备提取所需的内容
extracted_data = {}

for key, value in data.items():
    extracted_data[key] = {}
    for question, content in value.items():
        # 提取 p 和 answer 字段
        extracted_data[key][question] = {
            'p': content.get('p', ''),
            'answer': content.get('answer', '')
        }

# 将提取的内容保存为新的 JSON 文件
with open(output_file_path, 'w', encoding='utf-8') as outfile:
    json.dump(extracted_data, outfile, ensure_ascii=False, indent=4)

print(f'提取内容已保存为 {output_file_path}')
