import os
import json
import base64
import streamlit as st
from rag_agent import RAGAgent

# ===== 页面配置 =====
st.set_page_config(
    page_title="Dao AI - Answer your question in Chinese Wisdom",
    page_icon="🌮",
    layout="wide",  # Use full width layout for better visual appeal
    initial_sidebar_state="collapsed"  # Sidebar starts collapsed for a cleaner interface
)

# ===== 加载 base64 图片 =====
def image_to_base64(image_path):
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
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
                content: '';
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(255, 255, 255, 0.88);
                z-index: -1;
                pointer-events: none;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

# ===== 设置 Sidebar 背景 =====
def set_sidebar_background(image_path):
    bg_base64 = image_to_base64(image_path)
    if bg_base64:
        st.markdown(f"""
        <style>
        [data-testid="stSidebar"] {{
            background-image: url("data:image/png;base64,{bg_base64}");
            background-size: cover;
            background-position: center top;
            background-repeat: no-repeat;
            backdrop-filter: blur(6px);
            border-right: 1px solid rgba(0,0,0,0.05);
            font-family: 'Inter', sans-serif;
        }}
        [data-testid="stSidebar"] > div:first-child {{
            background: rgba(255,255,255,0.85);
            padding: 1rem;
            border-radius: 12px;
            margin: 1rem;
            font-family: 'Inter', sans-serif;
            font-size: 0.95rem;  /* 调整为稍小字体 */
        }}
        </style>
        """, unsafe_allow_html=True)

# ===== 现代字体和样式 =====
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
.stApp { font-family: 'Inter', sans-serif; }
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ===== 背景图 =====
set_background("水墨背景.png")
set_sidebar_background("装饰云彩.png")

# ===== 标题图标和文字 =====
dao_icon_base64 = image_to_base64("道icon.png")
if dao_icon_base64:
    st.markdown(f"""
    <div style="text-align:center; margin-bottom:2rem;">
        <img src="data:image/png;base64,{dao_icon_base64}" alt="道" style="width:120px; border-radius:50%;">
        <h1 style="font-size:3rem; font-weight:700;">Dao AI</h1>
        <p style="font-size:1.2rem; color:#4a5568;">Chinese Wisdom · Enrich Your Mind & Soul</p>
    </div>
    """, unsafe_allow_html=True)

# ===== 加载人物 personas.json =====
@st.cache_data(show_spinner=False)
def load_personas():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(current_dir, "personas.json"), "r", encoding="utf-8") as f:
        return json.load(f)

personas = load_personas()
mentor_names = list(personas.keys())

# ===== 左侧栏：选择导师 =====
with st.sidebar:
    st.markdown("**Choose Your Sage**")
    selected_mentor = st.selectbox("Select Sage", mentor_names, index=0)

# ===== 初始化 Agent（切换清空聊天） =====
if "selected_mentor" not in st.session_state:
    st.session_state.selected_mentor = selected_mentor
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "agent" not in st.session_state:
    st.session_state.agent = RAGAgent(persona=st.session_state.selected_mentor)

# ===== 显示聊天历史 =====
for msg in st.session_state.chat_history:
    with st.chat_message("user"):
        st.markdown(msg["question"])
    with st.chat_message("assistant", avatar="🌮"):
        st.markdown(msg["answer"])

# ===== 输入问题 =====
user_question = st.chat_input("Ask anything...")

if user_question:
    st.session_state.chat_history.append({"question": user_question, "answer": ""})
    st.rerun()

# ===== 回答逻辑 =====
if (
    "chat_history" in st.session_state and
    isinstance(st.session_state.chat_history, list) and
    len(st.session_state.chat_history) > 0 and
    isinstance(st.session_state.chat_history[-1], dict) and
    "answer" in st.session_state.chat_history[-1] and
    st.session_state.chat_history[-1]["answer"] == ""
):
    with st.spinner("Thinking..."):
        try:
            # 执行问答
            question = st.session_state.chat_history[-1]["question"]
            st.write("Sage is contemplating...", question)

            answer = st.session_state.agent.ask(question)
            st.session_state.chat_history[-1]["answer"] = answer
            st.rerun()

        except Exception as e:
            st.error(f"❌ Error in RAGAgent.ask: {str(e)}")
            st.session_state.chat_history[-1]["answer"] = f"Sage is meditating: {e}"
            st.rerun()

# ===== 页脚 =====
st.markdown("""
<div style="text-align:center; margin-top:3rem; color:#888888;">
    <p>道可道，非常道 · 名可名，非常名</p>
</div>
""", unsafe_allow_html=True)
