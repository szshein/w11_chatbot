# pages/world_cloud.py
import os, sys
import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from coding.utils import paging

# ── 如果需要，將專案根目錄加入 path（確保能 import coding.utils） ──
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# --- page setting ---
st.set_page_config(page_title="World Cloud", layout="wide")
st.title("☁️ World Cloud")

# --- sidebar ---
def save_lang():
    st.session_state['lang_setting'] = st.session_state.get("language_select")

user_image = "https://www.w3schools.com/howto/img_avatar.png"
with st.sidebar:
    paging()
    selected_lang = st.selectbox(
        "Language", ["English", "繁體中文"],
        index=1, on_change=save_lang, key="language_select"
    )
    st.session_state['lang_setting'] = st.session_state.get('lang_setting', selected_lang)
    st.image(user_image)

# --- load data ---
@st.cache_data
def load_data(path: str):
    return pd.read_csv(path)

df = load_data("104_jobs_all.csv")

# --- font path (請放入支援中文的 .ttf/.ttc 檔) ---
FONT_PATH = "msyh.ttc"
if not os.path.isfile(FONT_PATH):
    st.error(f"找不到字型檔：{FONT_PATH}，請放入專案根目錄")
    st.stop()

# --- 1. 所有職缺名稱文字雲 ---
st.header("所有職缺名稱文字雲")
all_names_text = " ".join(df["jobName"].astype(str).tolist())
wc_names = WordCloud(
    font_path=FONT_PATH, width=800, height=400,
    background_color="white", max_words=100
).generate(all_names_text)
fig1, ax1 = plt.subplots(figsize=(10, 5))
ax1.imshow(wc_names, interpolation="bilinear")
ax1.axis("off")
st.pyplot(fig1)

# --- 2. 所有職缺描述文字雲 ---
st.header("所有職缺描述文字雲")
all_desc_text = " ".join(df["description"].astype(str).tolist())
wc_desc = WordCloud(
    font_path=FONT_PATH, width=800, height=400,
    background_color="white", max_words=100
).generate(all_desc_text)
fig2, ax2 = plt.subplots(figsize=(10, 5))
ax2.imshow(wc_desc, interpolation="bilinear")
ax2.axis("off")
st.pyplot(fig2)

# --- 3. 單一職缺選擇並生成文字雲 ---
st.header("單一職缺文字雲展示")
job_list = df["jobName"].tolist()
selected = st.selectbox("請選擇職缺：", job_list)

content = df.loc[df["jobName"] == selected, "description"].values
if len(content) == 0:
    st.error("找不到對應的職缺描述！")
    st.stop()
single_text = content[0]

wc_single = WordCloud(
    font_path=FONT_PATH, width=800, height=400,
    background_color="white", max_words=100
).generate(single_text)
fig3, ax3 = plt.subplots(figsize=(10, 5))
ax3.imshow(wc_single, interpolation="bilinear")
ax3.axis("off")
st.pyplot(fig3)
