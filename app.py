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
    initial_sidebar_state="collapsed"
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

# ===== 顶部 LOGO 和 Slogan =====
dao_icon_base64 = image_to_base64("道icon.png")
if dao_icon_base64:
    st.markdown(f"""
    <div style="text-align:center; margin-bottom:3rem;">
        <img src="data:image/png;base64,{dao_icon_base64}" alt="道"
             style="width:140px; border-radius:50%; box-shadow: 0px 6px 15px rgba(0, 0, 0, 0.1);">
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

# ===== 左侧栏选择导师（简洁的下拉菜单） =====
with st.sidebar:
    st.markdown("""
        <h3 style="font-size:1.2rem; font-weight:600; color:#333;">Choose Your Sage</h3>
    """, unsafe_allow_html=True)
    
    # 使用简洁的下拉选择器
    selected_mentor = st.selectbox(
        "Select Sage", 
        mentor_names, 
        index=mentor_names.index(st.session_state.selected_mentor) if "selected_mentor" in st.session_state else 0
    )

# ===== 初始化 Agent =====
if selected_mentor != st.session_state.get("selected_mentor", ""):
    st.session_state.selected_mentor = selected_mentor
    st.session_state.agent = RAGAgent(persona=selected_mentor)
    st.session_state.chat_history = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "agent" not in st.session_state:
    st.session_state.agent = RAGAgent(persona=st.session_state.selected_mentor)

# ===== 获取导师头像（聊天气泡头像） =====
portrait_base64 = get_avatar_base64(st.session_state.selected_mentor)

# ===== 显示当前对话导师提示（融入背景版本） =====
st.markdown(f"""
<div style="text-align:center; margin:2rem 0 1rem; padding: 1.5rem 2rem; 
           background: linear-gradient(135deg, rgba(255,255,255,0.15), rgba(240,245,250,0.1)); 
           border: 1px solid rgba(255,255,255,0.2);
           border-radius: 30px; 
           backdrop-filter: blur(15px);
           box-shadow: 0 8px 32px rgba(0,0,0,0.08), 
                       0 1px 0 rgba(255,255,255,0.3) inset,
                       0 -1px 0 rgba(0,0,0,0.05) inset; 
           max-width: 450px; 
           margin-left: auto; margin-right: auto;
           position: relative;">
    <div style="font-size:1.3rem; font-weight:500; color:#2c3e50; margin-bottom: 0.8rem;
                text-shadow: 0 1px 3px rgba(255,255,255,0.9);">
        🧘 Chatting with {st.session_state.selected_mentor}
    </div>
    <div style="font-size:1rem; color:#5a6c7d;
                text-shadow: 0 1px 2px rgba(255,255,255,0.8);">
        Ask for ancient wisdom and guidance
    </div>
</div>
""", unsafe_allow_html=True)

# ===== 显示聊天历史 =====
for msg in st.session_state.chat_history:
    with st.chat_message("user", avatar=get_user_avatar()):
        st.markdown(msg["question"])
    with st.chat_message("assistant", avatar=portrait_base64):
        st.markdown(msg["answer"])

# ===== 输入问题 =====
user_question = st.chat_input("Ask anything...")
if user_question:
    st.session_state.chat_history.append({"question": user_question, "answer": ""})
    st.rerun()

# ===== 生成答案 =====
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
            question = st.session_state.chat_history[-1]["question"]
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
