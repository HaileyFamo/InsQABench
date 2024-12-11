import time
import streamlit as st
import pandas as pd
from transformers import AutoTokenizer, AutoModelForCausalLM
import dababase as db
from sqlalchemy import create_engine
import torch
st.set_page_config(page_title="InsLLM，智能数据库对话助手", page_icon=":speech_balloon:", layout="wide") # 设置页面标签
import re
import os
device = "cuda"
os.environ['CUDA_VISIBLE_DEVICES'] = '0,1,2'
# 定义页面样式和滚动行为
st.markdown(
    """<style>
.chat-message {
    padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem; display: flex
}
.chat-message.user {
    background-color: #2b313e
}
.chat-message.bot {
    background-color: #475063
}
.chat-message .avatar {
  width: 20%;
}
.chat-message .avatar img {
  max-width: 78px;
  max-height: 78px;
  border-radius: 50%;
  object-fit: cover;
}
.chat-message .message {
  width: 80%;
  padding: 0 1.5rem;
  color: #fff;
}
.stDeployButton {
            visibility: hidden;
        }
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

.block-container {
    padding: 2rem 4rem 2rem 4rem;
}

.st-emotion-cache-16txtl3 {
    padding: 3rem 1.5rem;
}
</style>
<script>
function scrollToBottom() {
    var chatContainer = document.querySelector('.block-container');
    chatContainer.scrollTop = chatContainer.scrollHeight;
}
</script>
# """,
    unsafe_allow_html=True,
)



# 机器人图标
bot_template = """
<div class="chat-message bot">
    <div class="avatar">
        <img src="https://img.icons8.com/?size=100&id=79UfeEN6JkZ8&format=png&color=000000" style="max-height: 50px; max-width: 50px; border-radius: 50%; object-fit: cover;">
    </div>
    <div class="message">{{MSG}}</div>
</div>
"""

# 用户图标
user_template = """
<div class="chat-message user">
    <div class="avatar">
        <img src="https://img.icons8.com/?size=100&id=23301&format=png&color=000000" style="max-height: 50px; max-width: 50px;">
    </div>    
    <div class="message">{{MSG}}</div>
</div>
"""


thought_prompt = """
你是一个保险领域的数据库分析工程师，下面是数据库中的信息，请你根据数据库表的信息,分析用户的问题,得到SQL语句，并根据查询到的结果回答用户问题。\n数据库中表的信息如下:\nCREATE TABLE \"保险公司\" (\n  \"公司编号\" INTEGER NOT NULL,\n  \"法定名称\" TEXT(255),\n  \"成立时间\" TEXT(255),\n  \"法定代表人\" TEXT(255),\n  \"官方网址\" TEXT(255),\n  \"公司住所\" TEXT(255),\n  \"注册资本(亿元人民币)\" REAL,\n  \"经营范围\" TEXT(255),\n  \"公司缩写\" TEXT(255),\n  \"公司类型\" TEXT(20),\n  \"所属公司编号\" INTEGER,\n  \"公司总机\" TEXT(20),\n  \"经营区域\" TEXT(240),\n  \"客服热线\" TEXT(20),\n  \"传真\" TEXT(28),\n  \"邮编\" TEXT(8),\n  \"营业场所\" TEXT(255),\n  PRIMARY KEY (\"公司编号\")\n),\nCREATE TABLE \"保险产品\" (\n  \"产品编号\" INTEGER NOT NULL,\n  \"产品名称\" TEXT(255),\n  \"产品类型\" TEXT(255),\n  \"特色\" TEXT(1100),\n  \"适宜人群\" TEXT(255),\n  \"产品网址\" TEXT(200),\n  \"责任免除\" TEXT(2100),\n  \"免赔金额（元人民币）\" TEXT(500),\n  \"保险期间\" TEXT(1000),\n  \"等待期\" TEXT(1000),\n  \"犹豫期\" TEXT(1200),\n  \"保险责任\" TEXT(2600),\n  \"交费方式/投保年龄\" TEXT(1000),\n  \"公司编号\" INTEGER,\n  \"销售状态\" TEXT(8),\n  \"红利\" TEXT(2000),\n  \"保单贷款\" TEXT(2400),\n  PRIMARY KEY (\"产品编号\"),\n  CONSTRAINT \"wai\" FOREIGN KEY (\"公司编号\") REFERENCES \"保险公司\" (\"公司编号\")\n)
如果是思考过程，用<Thought></Thought>包裹思考过程和<sql></sql>包裹生成的sql语句，只思考和生成sql一次。如果生成回答，则直接生成回答,不需要思考过程。
"""
ans_prompt = '''现在你应该直接生成回答，不需要生成thought和sql，回答的答案用<Answer></Answer>包裹.
要求:
    (1)你应该注意以客服的语气来写<Answer></Answer>。
    (2)所有回答的内容必须基于<exe></exe>的内容，不能够按照自己的知识回答Question
    (3)回答应该准确与严谨。比如，在查询过程中使用了模糊匹配，使查找到的结果可能与需要查询的产品名称不完全一样，这时候就不能简答的认为找到的答案就是用户想要的答案，
    你应该首先告诉用户我们没有找到完全一样的产品名称，但我们找到了相似的产品，接着回答后续的问题。如果使用了模糊匹配之后，查询到的结果中存在与用户Question中的
    实体名称完全一致的内容，就可以直接给出答复。不要完全按照上面的内容来回答，只需要表达准确相应的意思即可。
    (4)不能回答与Question无关的问题。
    (5)如果查询到了相似的结果,要回答你查询到的结果。不能直接回答没找到。'''


def get_db_link():
    # db_url = "mysql+pymysql://root:20020612fk@localhost/insurance"
    db_url = "sqlite:///insurance.db"
    engine = create_engine(db_url)
    return engine

def get_table_info(engine):
    query1 = "SHOW COLUMNS FROM `保险公司`"
    query2 = "SHOW COLUMNS FROM `保险产品`"
    with engine.connect() as connection:
        data1 = pd.read_sql(query1, connection)
        data2 = pd.read_sql(query2, connection)
    table_info = f"{data1}\n\n{data2}"
    return table_info


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
    return thoughts[0],sql[0]


# 调用模型生成回答
def get_response_from_model(dbs,model,tokenizer,history,user_question):

    response = react(dbs,model,tokenizer,history,user_question)

    return response

def react(dbs,model,tokenizer,history,user_question):
    inner_messages = history.copy()
    inner_messages.append({"role": "user", "content": thought_prompt+user_question})
    text = predict(model,tokenizer,inner_messages)

    count = 5
    while '<Answer>' not in text:
        if count == 0:
            break
        count -= 1
        thought,sql = get_thought_sql(text)
        sql = db.changesql(sql)

        sql_result = db.run_sql(dbs, sql)
        inner_messages.append({"role": "assistant", "content": f"<Thought>{thought}</Thought><sql>{sql}</sql>"})
        inner_messages.append({"role": "user", "content": f"下面是数据库中返回的结果:<exe>{sql_result}</exe>,请你继续分析"})

        text = predict(model, tokenizer, inner_messages)

    if '<Answer>' in text:
        answer = re.findall(r'<Answer>(.*?)</Answer>', text, re.DOTALL)[0]
    else:
        inner_messages[-1]['content'] += ans_prompt
        answer = predict(model, tokenizer, inner_messages)

    return answer.replace('<Answer>','').replace('</Answer>','')


# 根据用户的输入问题来处理
def handle_userinput_db(model,tokenizer,user_question):
    # 先打印用户的问题
    st.write(
        user_template.replace("{{MSG}}", user_question),
        unsafe_allow_html=True, # 允许在输出中使用HTML
    )

    chat_history = st.session_state.chat_history # 显示历史对话消息
    messages = []

    # 将历史对话转换为 HumanMessage 和 AIMessage 对象
    for role, content in chat_history:
        if role == "user":
            messages.append(("user",content))
        elif role == "assistant":
            messages.append(("assistant",content))


    full_content = st.empty()  # 创建一个可动态更新的占位符
    display_string = ""

    # 获取模型的响应
    dbs = get_db_link()
    model_response = get_response_from_model(dbs,model,tokenizer,messages,user_question)

    # 使用st.write_stream实现流式输出
    for char in model_response:
        display_string += char
        full_content.markdown(bot_template.replace("{{MSG}}", display_string), unsafe_allow_html=True)
        st.markdown("<script>scrollToBottom();</script>", unsafe_allow_html=True)
        time.sleep(0.02)  # 模拟延迟


    # 更新 chat_history
    st.session_state.chat_history.append(("user", user_question))
    st.session_state.chat_history.append(("assistant", display_string))


def show_history():
    chat_history = st.session_state.chat_history  # 获取历史的会话消息，并显示

    for i, message in enumerate(chat_history):
        if i % 2 == 0:
            st.write(
                user_template.replace("{{MSG}}", message[1]),
                unsafe_allow_html=True,
            )
        else:
            st.write(
                bot_template.replace("{{MSG}}", message[1]),
                unsafe_allow_html=True
            )

def main():
    # st.header("InsLLM，与您的保险合同对话。")
    st.header(":violet[_InsLLM_] ,智能数据库对话助手。")
    # 初始化会话状态
    if "conversation" not in st.session_state:
        st.session_state.conversation = []
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

        def clear_history():
            st.session_state.chat_history = []

        if st.session_state.chat_history:
            st.button("清空对话", on_click=clear_history, use_container_width=True)

    model,tokenizer = get_model()
    with st.container():
        user_question = st.chat_input("请输入您的问题")

    with st.container(height=500):
        show_history()
        if user_question:
            handle_userinput_db(model, tokenizer, user_question)

if __name__ == "__main__":
    main()




