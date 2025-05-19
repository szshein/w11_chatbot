import streamlit as st
import time
import json
from dotenv import load_dotenv
import os

# Import ConversableAgent class
import autogen
from autogen import ConversableAgent, LLMConfig, Agent
from autogen import AssistantAgent, UserProxyAgent, LLMConfig, register_function
from autogen.code_utils import content_str
from coding.constant import JOB_DEFINITION, RESPONSE_FORMAT
from coding.utils import (
    show_chat_history,
    display_session_msg,
    save_messages_to_json,
    paging,
)
from coding.agenttools import (
    AG_search_expert,
    AG_search_news,
    AG_search_textbook,
    get_time,
)

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import font_manager
from coding.utils import paging

# Load environment variables from .env file
load_dotenv(override=True)

# https://ai.google.dev/gemini-api/docs/pricing
# URL configurations
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", None)
OPEN_API_KEY = os.getenv("GEMINI_API_KEY", None)

placeholderstr = "Please input your command"
user_name = "Group 7"
user_image = "https://www.w3schools.com/howto/img_avatar.png"

seed = 42

llm_config_gemini = LLMConfig(
    api_type="google",
    model="gemini-2.0-flash",  # The specific model
    api_key=GEMINI_API_KEY,  # Authentication
)

llm_config_openai = LLMConfig(
    api_type="google",
    model="gemini-2.0-flash",  # The specific model
    api_key=OPEN_API_KEY,  # Authentication
)

# --- 載入與前處理資料 ---
def load_job_data():
    try:
        df = pd.read_csv("104_jobs_all.csv")
        df = df.dropna(subset=['jobName', 'description', 'jobAddrNoDesc'])
        return df
    except FileNotFoundError:
        st.error("找不到檔案：104_jobs_all.csv")
        return None

job_df = load_job_data()


def stream_data(stream_str):
    for word in stream_str.split(" "):
        yield word + " "
        time.sleep(0.05)


def save_lang():
    st.session_state["lang_setting"] = st.session_state.get("language_select")

def main():
    st.set_page_config(
        page_title="K-Assistant - The Residemy Agent",
        layout="wide",
        initial_sidebar_state="auto",
        menu_items={
            "Get Help": "https://streamlit.io/",
            "Report a bug": "https://github.com",
            "About": "About your application: **0.20.3.9**",
        },
        page_icon="img/favicon.ico",
    )

    # Show title and description.
    st.title(f"👩‍💼 Internship Navigator")

    with st.sidebar:
        paging()

        selected_lang = st.selectbox(
            "Language",
            ["English", "繁體中文"],
            index=0,
            on_change=save_lang,
            key="language_select",
        )
        if "lang_setting" in st.session_state:
            lang_setting = st.session_state["lang_setting"]
        else:
            lang_setting = selected_lang
            st.session_state["lang_setting"] = lang_setting

        st_c_1 = st.container(border=True)
        with st_c_1:
            st.image("https://www.w3schools.com/howto/img_avatar.png")

    st_c_chat = st.container(border=True)

    display_session_msg(st_c_chat, user_image)

    input_type = st.radio(
        "你想輸入的是？",
        ("感興趣的職缺", "你的技能"),
        horizontal=True,
        key="input_type",
    )

    student_persona = f"""You are a student willing to learn. After your result, say 'ALL DONE'. Please output in {lang_setting}"""

    teacher_persona = f"""You are a teacher. Please try to use tools to answer student's question according to the following rules:
    1. Check current time: use `get_time` tool to retrieve current date and time.
    2. Search news by `AG_search_news` according to user's question, try to distill student's question within 1~2 words and facilitate it as query string. Also you may search by sections,  e.g. ['Taiwan News', 'World News', 'Sports', 'Front Page', 'Features', 'Editorials', 'Business','Bilingual Pages'], if you cannot distill it, use None instead.
    3. From the return news, randomly pick one news. Classify the news to the following <DISCIPLINE>:
    <DISCIPLINE>
        "Digital Sociology"
        "Information Systems Strategy"
        "Technology and Society"
        "Empathetic and research-driven"
        "Computational Social Science"
    </DISCIPLINE>
    4. Use `AG_search_expert` to select expert by <DISCIPLINE>, also Use `AG_search_textbook` to select a textbook by <DISCIPLINE>.
    5. Explain to student a interesting essay within 500 words about the news using expert and textbook. Please remember to mention about the expert and textbook you cite.

    6. Fallback & Termination
        – On successful completion or when ending, return '##ALL DONE##'.
        - Return '##ALL DONE##' and respond accordingly when:
            • The task is completed.
            • The input is empty.
            • An error occurs.
            • The request is repeated.
            • Additional confirmation is required from the user.
    7. Please output in {lang_setting}
    """

    job_agent_persona = f"""
    你是一位實習職缺推薦老師。根據學生提供的實習職缺名稱，你要協助他們：

    1. 告訴他們「這份職缺通常需要哪些技能」。
    2. 告訴他們「可以去哪裡學這些技能」。
    3. 回答：「目前有哪些類似的職缺？」請從 `104_jobs_all.csv` 資料中篩選相關職缺。
    4. 如果學生說「我想在哪裡工作...」，請再根據地點進行篩選，回覆「這是根據你想工作地點進一步篩選後的職缺」。
    5. 若找不到職缺，請明確告知：「目前找不到相關的職缺喔」。

    請用簡單易懂的語言中文回覆，使用 {lang_setting}。在完成職缺推薦後，請說 'JOB_RECOMMENDATION_DONE'。
    """

    skill_agent_persona = f"""
    你是一位技能分析專家。當學生輸入他們擁有的技能時，你要：

    1. 告訴他們：「你可以做哪些實習類型（例如：資料分析、前端開發、行銷實習等）」。
    2. 根據學生說「我想朝 xxx 試看看」，針對該方向給出建議。
    3. 告訴他們：「除了你剛才說的技能，xxx 技能也很常見喔，加分喔！」（也就是建議加強的技能）。
    4. 接著回答：「現在有哪些適合的職缺？」請從 `104_jobs_all.csv` 找出符合技能條件的職缺。
    5. 如果學生說「我想在哪裡工作...」，請進一步根據地點篩選後回答：「這是根據你想工作地點進一步篩選後的職缺」。

    請使用 {lang_setting} 中文回答，並以鼓勵且實用的語氣與學生互動。在完成技能分析後，請說 'SKILL_ANALYSIS_DONE'。
    """


    with llm_config_gemini:
        teacher_agent = ConversableAgent(
            name="Teacher_Agent",
            system_message=teacher_persona,
        )

        job_advisor_agent = ConversableAgent(
            name="Job_Advisor_Agent",
            system_message=job_agent_persona,
        )

        skill_analyzer_agent = ConversableAgent(
            name="Skill_Analyzer_Agent",
            system_message=skill_agent_persona,
        )

    user_proxy = UserProxyAgent(
        "user_proxy",
        human_input_mode="NEVER",
        code_execution_config=False,
        is_termination_msg=lambda x: content_str(x.get("content")).find("##ALL DONE##")
        >= 0
        or content_str(x.get("content")).find("JOB_RECOMMENDATION_DONE") >= 0
        or content_str(x.get("content")).find("SKILL_ANALYSIS_DONE") >= 0,
    )

    def register_agent_methods(agent, proxy, methods):
        for name, description, func in methods:
            agent.register_for_llm(name=name, description=description)(func)
            proxy.register_for_execution(name=name)(func)

    methods_to_register = [
        ("get_time", "Retrieve the current date and time.", get_time),
        (
            "AG_search_expert",
            "Search EXPERTS_LIST by name, discipline, or interest.",
            AG_search_expert,
        ),
        (
            "AG_search_textbook",
            "Search TEXTBOOK_LIST by title, discipline, or related_expert.",
            AG_search_textbook,
        ),
        (
            "AG_search_news",
            "Search a pre-fetched news DataFrame by keywords, sections, and date range.",
            AG_search_news,
        ),
    ]

    # Register all methods using the helper function
    register_agent_methods(teacher_agent, user_proxy, methods_to_register)

    def generate_response(prompt, selected_input_type):
        if selected_input_type == "感興趣的職缺":
            chat_result = user_proxy.initiate_chat(
                job_advisor_agent,
                message=prompt,
            )
        elif selected_input_type == "你的技能":
            chat_result = user_proxy.initiate_chat(
                skill_analyzer_agent,
                message=prompt
            )
        else:
            chat_result = user_proxy.initiate_chat(
                teacher_agent,
                message=prompt,
            )
        response = chat_result.chat_history
        return response

    def chat(prompt: str, input_type: str):
        response = generate_response(prompt, input_type)
        show_chat_history(st_c_chat, response, user_image)
        # messages = json.loads(conv_res)
        # file_path = save_messages_to_json(messages, output_dir="chat_logs")
        # st.write(f"Saved chat history to `{file_path}`")

    if prompt := st.chat_input(placeholder=placeholderstr, key="chat_bot"):
        chat(prompt, st.session_state.input_type)


if __name__ == "__main__":
    main()
