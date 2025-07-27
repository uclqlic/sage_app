import os
import json
import base64
import streamlit as st
from rag_agent import RAGAgent

# ===== 页面配置 =====
st.set_page_config(
    page_title="Dao AI - Answer your question in Chinese Wisdom",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== 加载 base64 图片 =====
def image_to_base64(image_path):
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return None

def get_avatar_base64(name: str):
    path = os.path.join("persona_protrait", f"{name}.png")
    if os.path.exists(path):
        with open(path, "rb") as f:
            return "data:image/png;base64," + base64.b64encode(f.read()).decode()
    fallback = os.path.join("persona_protrait", "bot_icon.png")
    if os.path.exists(fallback):
        with open(fallback, "rb") as f:
            return "data:image/png;base64," + base64.b64encode(f.read()).decode()
    return None

def get_user_avatar():
    path = os.path.join("persona_protrait", "user_icon.png")
    if os.path.exists(path):
        with open(path, "rb") as f:
            return "data:image/png;base64," + base64.b64encode(f.read()).decode()
    return None

# ===== 设置背景 =====
def set_background(image_path):
    bg_base64 = image_to_base64(image_path)
    if bg_base64:
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{bg_base64}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
            }}
            .stApp::before {{
                content: ''; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                background: rgba(255, 255, 255, 0.7); z-index: -1; pointer-events: none;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

def set_sidebar_background(image_path):
    bg_base64 = image_to_base64(image_path)
    if bg_base64:
        st.markdown(f"""
        <style>
        [data-testid="stSidebar"] {{
            background-image: url("data:image/png;base64,{bg_base64}");
            background-size: cover; background-position: center top; background-repeat: no-repeat;
            backdrop-filter: blur(8px); border-right: 1px solid rgba(0,0,0,0.1);
            font-family: 'Inter', sans-serif;
        }}
        [data-testid="stSidebar"] > div:first-child {{
            background: rgba(255,255,255,0.9); padding: 1.5rem; border-radius: 15px;
            margin: 1.5rem; font-family: 'Inter', sans-serif; font-size: 1rem;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        }}
        .mentor-card:hover {{
            transform: scale(1.05);
            transition: 0.3s ease;
            cursor: pointer;
        }}
        </style>
        """, unsafe_allow_html=True)

# ===== 字体样式 =====
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
.stApp { font-family: 'Inter', sans-serif; line-height: 1.6; }
#MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ===== 背景图 =====
set_background("水墨背景.png")
set_sidebar_background("装饰云彩.png")

# ===== 加载人物 personas.json =====
@st.cache_data(show_spinner=False)
def load_personas():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(current_dir, "personas.json"), "r", encoding="utf-8") as f:
        return json.load(f)

personas = load_personas()
mentor_names = list(personas.keys())

# ===== 左侧栏选择导师卡片风格 =====
with st.sidebar:
    st.markdown("""
        <h3 style="font-size:1.2rem; font-weight:600; color:#333;">选择一位智慧导师</h3>
    """, unsafe_allow_html=True)
    cols = st.columns(2)
    for idx, name in enumerate(mentor_names):
        avatar = get_avatar_base64(name)
        if avatar:
            if cols[idx % 2].button(
                f"\n\n<div class='mentor-card' style='text-align:center;'>"
                f"<img src='{avatar}' style='width:70px; height:70px; border-radius:50%;'><br><span style='font-size:0.95rem;'>{name}</span>"
                f"</div>",
                key=name,
                use_container_width=True,
                help=f"与{name}交谈",
                type="secondary"
            ):
                st.session_state.selected_mentor = name
                st.session_state.agent = RAGAgent(persona=name)
                st.session_state.chat_history = []

# ===== 初始化 Agent =====
if "selected_mentor" not in st.session_state:
    st.session_state.selected_mentor = mentor_names[0]
    st.session_state.agent = RAGAgent(persona=st.session_state.selected_mentor)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ===== 获取导师头像 =====
portrait_base64 = get_avatar_base64(st.session_state.selected_mentor)

# ===== 对话顶部提示 =====
st.markdown(f"""
<div style="text-align:center; margin-top:2rem; font-size:1.1rem; color:#555;">
    当前对话：<strong>{st.session_state.selected_mentor}</strong>
</div>
""", unsafe_allow_html=True)

# ===== 聊天记录显示 =====
for msg in st.session_state.chat_history:
    with st.chat_message("user", avatar=get_user_avatar()):
        st.markdown(msg["question"])
    with st.chat_message("assistant", avatar=portrait_base64):
        st.markdown(msg["answer"])

# ===== 输入问题 =====
user_question = st.chat_input("问你想问的一切……")
if user_question:
    st.session_state.chat_history.append({"question": user_question, "answer": ""})
    st.rerun()

# ===== 回答生成逻辑 =====
if (
    "chat_history" in st.session_state and
    isinstance(st.session_state.chat_history, list) and
    len(st.session_state.chat_history) > 0 and
    isinstance(st.session_state.chat_history[-1], dict) and
    "answer" in st.session_state.chat_history[-1] and
    st.session_state.chat_history[-1]["answer"] == ""
):
    with st.spinner("导师沉思中……"):
        try:
            question = st.session_state.chat_history[-1]["question"]
            answer = st.session_state.agent.ask(question)
            st.session_state.chat_history[-1]["answer"] = answer
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error in RAGAgent.ask: {str(e)}")
            st.session_state.chat_history[-1]["answer"] = f"导师沉思中：{e}"
            st.rerun()

# ===== 页脚 =====
st.markdown("""
<div style="text-align:center; margin-top:4rem; color:#777;">
    <p>道可道，非常道 · 名可名，非常名</p>
</div>
""", unsafe_allow_html=True)
