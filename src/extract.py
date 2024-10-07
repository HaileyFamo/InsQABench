# -*- coding: utf-8 -*-
import os
import json

def get_para_json_unified(input_dir, output_dir):
    
    os.makedirs(output_dir, exist_ok=True)
    def is_paragraph_start(text):
        """
        Determine if the given text marks the start of a new paragraph.
        """
        return text.startswith('1.1') or text.startswith('第一条') or text.startswith('一、') or text.startswith('第一章')

    def paragraph_continuation(prev_bounds, current_bounds, prev_page, current_page):
        """
        Determine if the current text element continues the previous paragraph based on bounds and page number.
        """
        vertical_distance = current_bounds[1] - prev_bounds[3]
        horizontal_distance = abs(current_bounds[0] - prev_bounds[0])

        return (vertical_distance < 50 or (current_page == prev_page + 1)) and horizontal_distance < 10

    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.json'):
                relative_path = os.path.relpath(root, input_dir)
                temp_name = relative_path.split(os.sep)[-2:]

               
                print(len(temp_name))
                if len("".join(temp_name)) > 60 and len(temp_name)  > 1:
                    temp_name = [temp_name[1]]

                par_name = "-".join(temp_name)
                par_name = os.path.basename(input_dir) + '-' + par_name

                save_path = os.path.join(output_dir, f'{par_name}.json')
                if os.path.exists(save_path):
                    print("Exist. Skip.")
                    continue
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    data = json.load(f)

                    paras = []  
                    cur_para = {"页码": None, "内容": ""}
                    prev_bounds = [0, 0, 0, 0]  
                    prev_page = 0 

                    for ele in data['elements']:
                        if not ele.get('Text'):
                            continue

                        if is_paragraph_start(ele["Text"]):
                            if cur_para["内容"]:  
                                paras.append(cur_para)
                            cur_para = {"页码": ele["Page"], "内容": ele["Text"]}
                            prev_bounds = ele["Bounds"]
                            prev_page = ele['Page']
                        elif paragraph_continuation(prev_bounds, ele["Bounds"], prev_page, ele['Page']):
                            cur_para["内容"] += " " + ele["Text"]
                        else:
                            if cur_para["内容"]:  
                                paras.append(cur_para)
                            cur_para = {"页码": ele["Page"], "内容": ele["Text"]}

                        prev_bounds = ele["Bounds"]
                        prev_page = ele['Page']

                    if cur_para["内容"]:
                        paras.append(cur_para)

                try:
                    with open(save_path, 'w', encoding='utf-8') as f_out:
                        for para in paras:
                            json_string = json.dumps(para, ensure_ascii=False)
                            f_out.write(json_string + '\n')
                except Exception as e:
                    print(e)


if __name__ == '__main__':
    pass