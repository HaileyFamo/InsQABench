aspect_descriptions = {
    "accuracy": (
        "The content of pending scored answer conforms to the insurance term,"
        "especially note the answer should be based on the specific content in the term. Too general answers are not accurate. "
        "If a model answer the question in a correct but more precise way, it should get higher score."
    ),
    "completeness": (
        "Compared to the term, pending scored answer does not miss any details. "
        "A answer with solid details from the term instead of general explanation should get higher score."

    ),
    "clarity": (
        "the logic of pending scored answer is rigorous and clear, and the sentences are easy for the customer who are unfamilar to insurance to understand. The answer that notes and explains the professional nouns should get higher scores. "
        "If Accuracy and Completeness is bad, Clarity should also be bad."
    )
}


def get_new_a_pmt(question, material):
    return f"""
    You are a professional, impartial, and strict scorer who is qualified in Chinese Insurance field. You are going to answer a question from a consumer knows nothing about the insurance field.
    You will be given a question and a paragraph of a term where the question is derived from. 
    Please give an answer based on the given material.
    Requirements:
    The answer should be as detailed as possible, and be easy for a consumer to understand.
    Give the evidence of where you find the answer. 
    You should also give explantions about the terms in the question and the answer.
    In your response, you should only include the answer. Do not include any additional information or explanation. 
    Desire output:
    [答案]: ...
    [证据]: (Insert the evidence from the material)
    [Inserting the explanation for a specific professional word]: ...
    
    material:{material}\n
    question:{question}   
    """ 
    
    
def get_eval_pmt(question, material, answer, model_answers):

    return f"""
    You are a professional, impartial, and strict scorer who is qualified in Chinese Insurance field. 
        You will be given a question,a paragraph of a term where the question is derived from,7 pending scored answers from different models.Please rate the pending scored answers based on the reference answer in the following aspects:\n{aspect_descriptions}\n\nEach score should be from 1(lowest)-100(highest),the minimum unit of score is 1.Your rating should be strict enough,and do not easily give full scores! In scoring, ensure differentiation among similar scores by closely comparing the detail level of answers within the same score range. In your response,you should only include a JSON object,with a python dict with keys being 'model 1' to 'model 7', and their values are also dict with keys being the aspects and values being the scores.Do not include any additional information or explanation.
        ### Question\n```\n{question}\n```\n\n### Paragraph in term\n```\n
        {material}\n```\n\n### Paragraph in term\n```\n{answer}\n```\n\n### Pending scored answers from different model:\n```\n{model_answers}\n```
    """