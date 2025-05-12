import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from coding.utils import paging

# --- page setting ---
st.set_page_config(page_title="World Cloud", layout="wide")
st.title("☁️ World Cloud")

def save_lang():
    st.session_state['lang_setting'] = st.session_state.get("language_select")

user_image = "https://www.w3schools.com/howto/img_avatar.png"
with st.sidebar:
        paging()
        selected_lang = st.selectbox("Language", ["English", "繁體中文"], index=1, on_change=save_lang, key="language_select")

        lang_setting = st.session_state.get('lang_setting', selected_lang)
        st.session_state['lang_setting'] = lang_setting

        st_c_1 = st.container(border=True)
        with st_c_1:
            st.image(user_image)
     
# --- load data ---
@st.cache_data(show_spinner=False)
def load_data(path: str):
    return pd.read_csv(path)

df = load_data("104_jobs_all.csv")

# --- user command ---
job_list = df["jobName"].tolist()
selected = st.selectbox("請選擇職缺：", job_list)

# --- world cloud ---
content = df.loc[df["jobName"] == selected, "description"].values
if len(content) == 0:
    st.error("找不到對應的職缺描述！")
    st.stop()
text = content[0]

# --- generate ---
font_path = "msyh.ttc"  
wc = WordCloud(
    font_path=font_path,
    width=800,
    height=400,
    background_color="white",
    max_words=100
)
wc.generate(text)

# --- show plot ---
fig, ax = plt.subplots(figsize=(10, 5))
ax.imshow(wc, interpolation="bilinear")
ax.axis("off")
st.pyplot(fig)