# app.py
import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# --- page setting ---
st.set_page_config(page_title="World Cloud", layout="wide")
st.title("☁️ World Cloud")

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
font_path = "/workspaces/w11_chatbot/msyh.ttc"  
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