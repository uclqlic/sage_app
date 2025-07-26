import os
import json
import base64
import streamlit as st
from rag_agent import RAGAgent

# ===== 页面配置 =====
st.set_page_config(
    page_title="Dao AI - Answer your question in Chinese Wisdom",
    page_icon="",
    layout="wide",  # 使用全宽布局，增强视觉效果
    initial_sidebar_state="collapsed"  # 初始侧边栏收起，清爽简洁
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
                background: rgba(255, 255, 255, 0.7);  /* 半透明效果 */
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
            backdrop-filter: blur(8px); /* 增强模糊效果 */
            border-right: 1px solid rgba(0,0,0,0.1); /* 更清晰的边框 */
            font-family: 'Inter', sans-serif;
        }}
        [data-testid="stSidebar"] > div:first-child {{
            background: rgba(255,255,255,0.9);
            padding: 1.5rem;
            border-radius: 15px;  /* 圆角 */
            margin: 1.5rem;
            font-family: 'Inter', sans-serif;
            font-size: 1rem;  /* 增加字体大小 */
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); /* 增加阴影 */
        }}
        </style>
        """, unsafe_allow_html=True)

# ===== 现代字体和样式 =====
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
.stApp { font-family: 'Inter', sans-serif; line-height: 1.6; }
#MainMenu {visibility: hidden;}  /* 隐藏菜单 */
footer {visibility: hidden;}  /* 隐藏页脚 */
</style>
""", unsafe_allow_html=True)

# ===== 背景图 =====
set_background("水墨背景.png")
set_sidebar_background("装饰云彩.png")

# ===== 标题图标和文字 =====
dao_icon_base64 = image_to_base64("道icon.png")
if dao_icon_base64:
    st.markdown(f"""
    <div style="text-align:center; margin-bottom:3rem;">
        <img src="data:image/png;base64,{dao_icon_base64}" alt="道" style="width:140px; border-radius:50%; box-shadow: 0px 6px 15px rgba(0, 0, 0, 0.1);">
        <h1 style="font-size:3.5rem; font-weight:800; color:#333;">Dao AI</h1>
        <p style="font-size:1.4rem; color:#555;">Chinese Wisdom · Enrich Your Mind & Soul</p>
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
    st.markdown("""
        <h3 style="font-size:1.2rem; font-weight:600; color:#333;">Choose Your Sage</h3>
    """, unsafe_allow_html=True)
    selected_mentor = st.selectbox("Select Sage", mentor_names, index=mentor_names.index(st.session_state.selected_mentor) if "selected_mentor" in st.session_state else 0)

# ===== 如果选定的导师发生变化，则重新创建 RAGAgent 实例 =====
if selected_mentor != st.session_state.get("selected_mentor", ""):
    st.session_state.selected_mentor = selected_mentor
    st.session_state.agent = RAGAgent(persona=selected_mentor)
    st.session_state.chat_history = []  # 清空聊天历史

# ===== 初始化 Agent（切换清空聊天） =====
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "agent" not in st.session_state:
    st.session_state.agent = RAGAgent(persona=st.session_state.selected_mentor)

# ===== 显示聊天历史 =====
for msg in st.session_state.chat_history:
    with st.chat_message("user"):
        st.markdown(msg["question"])
    with st.chat_message("assistant"):
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
    with st.spinner("The sage is reflecting..."):
        try:
            # 执行问答
            question = st.session_state.chat_history[-1]["question"]
            st.write(f"<i>The sage is contemplating...</i><br>{question}", unsafe_allow_html=True)

            answer = st.session_state.agent.ask(question)
            st.session_state.chat_history[-1]["answer"] = answer
            st.rerun()

        except Exception as e:
            st.error(f"❌ Error in RAGAgent.ask: {str(e)}")
            st.session_state.chat_history[-1]["answer"] = f"The sage is reflecting: {e}"
            st.rerun()

# ===== 页脚 =====
st.markdown("""
<div style="text-align:center; margin-top:4rem; color:#777;">
    <p>道可道，非常道 · 名可名，非常名</p>
</div>
""", unsafe_allow_html=True)
