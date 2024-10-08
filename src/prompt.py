pmt3 = """
问题/任务描述：
作为一位中国保险领域的专家，你需要根据提供的保险文档材料，回答消费者提出的3个关于保险合同内容的问题。这些问题是基于消费者对材料的理解和好奇心提出的，可能涉及到从材料中复杂推理而来的内容。你的回答应该具体、详细，并基于材料内容给出解释。使用的语言应该是礼貌、专业但简单的，以便于保险初学者能够理解。同时，对问题和答案中出现的所有专有名词进行解释，并确保所有的回答都能直接通过材料找到答案，不引入材料之外的信息。请注意，每个回答应该与相应的问题相匹配，且问题已经通过一个简答题的形式提出。
要求：
1. 阅读并理解消费者基于所提供材料提出的问题。如果无法提出有效的问题，直接回答：跳过
2. 提供详细、具体的回答，直接基于材料的内容。
3. 使用简单、易懂的语言回答问题，确保非专业人士也能理解。
4. 对材料中的所有专有名词，即日常用语中不会出现的词语给出清晰的解释。
5. 确保回答仅依据所提供的材料，并且准确反映材料内容。
6. 每个回答应独立完成，针对每个问题提供一个专业的解答。再次确保，在每个回答中，都有对问题和答案的专有名词进行解释。
输出格式（使用Markdown语法加粗问题和回答标识）：（如果之前选择跳过，忽略此格式，输出“跳过”两个字。）
**[Q1]**: [消费者的第一个问题]
**[A1]**: [根据材料内容对第一个问题的详细回答，**专有名词解释**：如果有专有名词，列出并解释]
**[Q2]**: [消费者的第二个问题]
**[A2]**: [根据材料内容对第二个问题的详细回答，**专有名词解释**：如果有专有名词，列出并解释]
**[Q3]**: [消费者的第三个问题]
**[A3]**: [根据材料内容对第三个问题的详细回答，**专有名词解释**：如果有专有名词，列出并解释]

下面是材料：
"""

pmt2 = """
问题/任务描述：
作为一位中国保险领域的专家，你需要根据提供的保险文档材料，回答消费者提出的2个关于保险合同内容的问题。这些问题是基于消费者对材料的理解和好奇心提出的，可能涉及到从材料中复杂推理而来的内容。你的回答应该具体、详细，并基于材料内容给出解释。使用的语言应该是礼貌、专业但简单的，以便于保险初学者能够理解。同时，对问题和答案中出现的所有专有名词进行解释，并确保所有的回答都能直接通过材料找到答案，不引入材料之外的信息。请注意，每个回答应该与相应的问题相匹配，且问题已经通过一个简答题的形式提出。
要求：
1. 阅读并理解消费者基于所提供材料提出的问题。如果无法提出有效的问题，直接回答：跳过
2. 提供详细、具体的回答，直接基于材料的内容。
3. 使用简单、易懂的语言回答问题，确保非专业人士也能理解。
4. 对材料中的所有专有名词，即日常用语中不会出现的词语给出清晰的解释。
5. 确保回答仅依据所提供的材料，并且准确反映材料内容。
6. 每个回答应独立完成，针对每个问题提供一个专业的解答。再次确保，在每个回答中，都有对问题和答案的专有名词进行解释。
输出格式（使用Markdown语法加粗问题和回答标识）：（如果之前选择跳过，忽略此格式，输出“跳过”两个字。）
**[Q1]**: [消费者的第一个问题]
**[A1]**: [根据材料内容对第一个问题的详细回答，**专有名词解释**：如果有专有名词，列出并解释]
**[Q2]**: [消费者的第二个问题]
**[A2]**: [根据材料内容对第二个问题的详细回答，**专有名词解释**：如果有专有名词，列出并解释]

下面是材料：
"""

pmt1 = """
问题/任务描述：
作为一位中国保险领域的专家，你需要根据提供的保险文档材料，回答消费者提出的1个关于保险合同内容的问题。这些问题是基于消费者对材料的理解和好奇心提出的，可能涉及到从材料中复杂推理而来的内容。你的回答应该具体、详细，并基于材料内容给出解释。使用的语言应该是礼貌、专业但简单的，以便于保险初学者能够理解。同时，对问题和答案中出现的所有专有名词进行解释，并确保所有的回答都能直接通过材料找到答案，不引入材料之外的信息。请注意，每个回答应该与相应的问题相匹配，且问题已经通过一个简答题的形式提出。
要求：
1. 阅读并理解消费者基于所提供材料提出的问题。如果无法提出有效的问题，直接回答：跳过
2. 提供详细、具体的回答，直接基于材料的内容。
3. 使用简单、易懂的语言回答问题，确保非专业人士也能理解。
4. 对材料中的所有专有名词，即日常用语中不会出现的词语给出清晰的解释。
5. 确保回答仅依据所提供的材料，并且准确反映材料内容。
6. 每个回答应独立完成，针对每个问题提供一个专业的解答。再次确保，在每个回答中，都有对问题和答案的专有名词进行解释。
输出格式（使用Markdown语法加粗问题和回答标识）：（如果之前选择跳过，忽略此格式，输出“跳过”两个字。）
**[Q1]**: [消费者的问题]
**[A1]**: [根据材料内容对问题的详细回答，**专有名词解释**：如果有专有名词，列出并解释]

下面是材料：
"""
