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

# ===== 协调的字体和全局样式 =====
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@400;500;600;700&family=Noto+Serif:wght@300;400;500&display=swap');

/* 全局样式 */
.stApp { 
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; 
    line-height: 1.6; 
    color: #2c3e50;
}

/* 隐藏默认元素 */
#MainMenu {visibility: hidden;} 
footer {visibility: hidden;}
.stDeployButton {display: none;}

/* 全局文字颜色协调 */
.stApp, .stApp p, .stApp div {
    color: #2c3e50 !important;
}

/* 主标题样式 */
h1 {
    font-family: 'Playfair Display', serif !important;
    font-weight: 600 !important;
    color: #1a202c !important;
    letter-spacing: -0.02em !important;
}

/* 副标题样式 */
.subtitle {
    font-family: 'Noto Serif', serif !important;
    font-weight: 400 !important;
    color: #4a5568 !important;
    letter-spacing: 0.01em !important;
}

/* 侧边栏标题 */
.stSidebar h3 {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    color: #2d3748 !important;
    font-size: 1.1rem !important;
}

/* 选择框样式 */
.stSelectbox label {
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    color: #4a5568 !important;
    font-size: 0.9rem !important;
}

/* 聊天消息样式 */
.stChatMessage {
    font-family: 'Inter', sans-serif !important;
}

/* 输入框样式 */
.stChatInput input {
    font-family: 'Inter', sans-serif !important;
    color: #2d3748 !important;
}

/* 页脚样式 */
.footer-text {
    font-family: 'Noto Serif', serif !important;
    font-weight: 300 !important;
    color: #718096 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.05em !important;
}
</style>
""", unsafe_allow_html=True)

# ===== 背景图 =====
set_background("水墨背景.png")
set_sidebar_background("装饰云彩.png")

# ===== 顶部 LOGO 和 Slogan（协调版本） =====
dao_icon_base64 = image_to_base64("道icon.png")
if dao_icon_base64:
    st.markdown(f"""
    <div style="text-align:center; margin-bottom:3rem;">
        <img src="data:image/png;base64,{dao_icon_base64}" alt="道"
             style="width:120px; border-radius:50%; box-shadow: 0px 8px 25px rgba(0, 0, 0, 0.12); margin-bottom: 1.5rem;">
        <h1 style="font-family: 'Playfair Display', serif; font-size:3.2rem; font-weight:600; 
                   color:#1a202c; margin-bottom: 0.8rem; letter-spacing: -0.02em;
                   text-shadow: 0 2px 4px rgba(255,255,255,0.8);">
            Dao AI
        </h1>
        <p class="subtitle" style="font-family: 'Noto Serif', serif; font-size:1.2rem; font-weight:400;
                                   color:#4a5568; margin: 0; letter-spacing: 0.01em;
                                   text-shadow: 0 1px 2px rgba(255,255,255,0.7);">
            Chinese Wisdom · Enrich Your Mind & Soul
        </p>
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

# ===== 左侧栏选择导师（协调版本） =====
with st.sidebar:
    st.markdown("""
        <h3 style="font-family: 'Inter', sans-serif; font-size:1.1rem; font-weight:600; 
                   color:#2d3748; margin-bottom: 1rem; letter-spacing: -0.01em;">
            Choose Your Sage
        </h3>
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

# ===== 显示当前对话导师提示（协调版本） =====
st.markdown(f"""
<div style="text-align:center; margin:2rem 0 1rem; padding: 1.8rem 2.5rem; 
           background: linear-gradient(135deg, rgba(255,255,255,0.12), rgba(248,250,252,0.08)); 
           border: 1px solid rgba(255,255,255,0.18);
           border-radius: 32px; 
           backdrop-filter: blur(18px);
           box-shadow: 0 8px 32px rgba(0,0,0,0.06), 
                       0 1px 0 rgba(255,255,255,0.25) inset,
                       0 -1px 0 rgba(0,0,0,0.04) inset; 
           max-width: 480px; 
           margin-left: auto; margin-right: auto;
           position: relative;">
    <div style="font-family: 'Inter', sans-serif; font-size:1.25rem; font-weight:500; 
                color:#1a202c; margin-bottom: 0.7rem; letter-spacing: -0.01em;
                text-shadow: 0 1px 3px rgba(255,255,255,0.9);">
        💭 Chatting with {st.session_state.selected_mentor}
    </div>
    <div style="font-family: 'Noto Serif', serif; font-size:0.95rem; font-weight:400;
                color:#4a5568; letter-spacing: 0.01em;
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

# ===== 输入问题（协调版本） =====
user_question = st.chat_input("Share your thoughts and seek wisdom...")
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

# ===== 页脚（协调版本） =====
st.markdown("""
<div style="text-align:center; margin-top:4rem; padding-top: 2rem;">
    <p class="footer-text" style="font-family: 'Noto Serif', serif; font-weight:300; 
                                  color:#718096; font-size:0.9rem; letter-spacing: 0.05em;
                                  text-shadow: 0 1px 2px rgba(255,255,255,0.6);">
        道可道，非常道 · 名可名，非常名
    </p>
</div>
""", unsafe_allow_html=True)
