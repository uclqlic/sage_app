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

# ===== 设置背景（优化可读性） =====
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
                background: rgba(255, 255, 255, 0.85); z-index: -1; pointer-events: none;
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
        
        /* 细微优化的卡片样式 */
        .sage-card {{
            display: flex; align-items: center; padding: 0.9rem; margin: 0.7rem 0;
            border-radius: 14px; cursor: pointer; transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            background: rgba(255,255,255,0.85); border: 1.5px solid rgba(226, 232, 240, 0.6);
            backdrop-filter: blur(10px);
        }}
        
        .sage-card:hover {{
            background: rgba(255,255,255,0.95); border-color: #4a6fa5;
            transform: translateY(-1px); box-shadow: 0 6px 16px rgba(74, 111, 165, 0.15);
        }}
        
        .sage-card.selected {{
            background: linear-gradient(135deg, rgba(74, 111, 165, 0.08), rgba(45, 74, 107, 0.04));
            border-color: #4a6fa5; box-shadow: 0 6px 20px rgba(74, 111, 165, 0.2);
        }}
        
        .sage-avatar {{
            width: 50px; height: 50px; border-radius: 50%; margin-right: 0.9rem;
            object-fit: cover; border: 2.5px solid rgba(255,255,255,0.8);
            box-shadow: 0 3px 10px rgba(0,0,0,0.12); transition: all 0.25s ease;
        }}
        
        .sage-card.selected .sage-avatar {{
            border-color: rgba(74, 111, 165, 0.4);
            box-shadow: 0 0 0 2px rgba(74, 111, 165, 0.15);
        }}
        
        .sage-name {{
            font-size: 1.05rem; font-weight: 600; color: #2d3748; line-height: 1.3;
        }}
        
        .sage-card.selected .sage-name {{
            color: #4a6fa5;
        }}
        </style>
        """, unsafe_allow_html=True)

# ===== 细微优化的字体样式（增强可读性和聊天区分） =====
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@400;500;600;700&family=Noto+Serif:wght@300;400;500&display=swap');

.stApp { 
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; 
    line-height: 1.6; color: #2c3e50;
}

#MainMenu {visibility: hidden;} 
footer {visibility: hidden;}
.stDeployButton {display: none;}

/* 主标题优化 */
h1 {
    font-family: 'Playfair Display', serif !important;
    font-weight: 600 !important;
    color: #1a202c !important;
    letter-spacing: -0.015em !important;
    text-shadow: 0 2px 4px rgba(255,255,255,0.9) !important;
}

/* 副标题优化 */
.subtitle {
    font-family: 'Noto Serif', serif !important;
    font-weight: 400 !important;
    color: #4a5568 !important;
    letter-spacing: 0.01em !important;
    text-shadow: 0 1px 2px rgba(255,255,255,0.8) !important;
}

/* 侧边栏标题优化 */
.stSidebar h3 {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    color: #2d3748 !important;
    font-size: 1.15rem !important;
    letter-spacing: -0.01em !important;
}

/* 聊天消息区域优化 - 增强对比度和区分度 */
.stChatMessage {
    margin: 1.5rem 0 !important;
    border-radius: 16px !important;
    padding: 0 !important;
}

/* 用户消息样式 */
.stChatMessage[data-testid*="user"] {
    background: rgba(74, 111, 165, 0.08) !important;
    border: 1px solid rgba(74, 111, 165, 0.15) !important;
    margin-left: 2rem !important;
    box-shadow: 0 2px 8px rgba(74, 111, 165, 0.1) !important;
}

/* AI消息样式 */
.stChatMessage[data-testid*="assistant"] {
    background: rgba(255, 255, 255, 0.95) !important;
    border: 1px solid rgba(226, 232, 240, 0.8) !important;
    margin-right: 2rem !important;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08) !important;
}

/* 消息内容文字优化 */
.stChatMessage .stMarkdown {
    color: #2d3748 !important;
    font-weight: 400 !important;
    line-height: 1.6 !important;
    padding: 1rem 1.5rem !important;
}

/* 用户消息文字 */
.stChatMessage[data-testid*="user"] .stMarkdown {
    color: #1e40af !important;
    font-weight: 500 !important;
}

/* AI消息文字 */
.stChatMessage[data-testid*="assistant"] .stMarkdown {
    color: #374151 !important;
    font-family: 'Noto Serif', serif !important;
}

/* 聊天输入框优化 */
.stChatInputContainer {
    background: rgba(255, 255, 255, 0.95) !important;
    border-radius: 18px !important;
    border: 2px solid rgba(74, 111, 165, 0.2) !important;
    backdrop-filter: blur(12px) !important;
    box-shadow: 0 4px 16px rgba(0,0,0,0.1) !important;
    transition: all 0.25s ease !important;
}

.stChatInputContainer:focus-within {
    border-color: #4a6fa5 !important;
    box-shadow: 0 0 0 3px rgba(74, 111, 165, 0.15), 0 6px 20px rgba(0,0,0,0.15) !important;
    transform: translateY(-1px) !important;
}

.stChatInput input {
    color: #2d3748 !important;
    font-weight: 400 !important;
    font-size: 1rem !important;
}

.stChatInput input::placeholder {
    color: #6b7280 !important;
    font-style: italic !important;
}

/* 页脚优化 */
.footer-text {
    font-family: 'Noto Serif', serif !important;
    font-weight: 300 !important;
    color: #718096 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.03em !important;
    text-shadow: 0 1px 2px rgba(255,255,255,0.8) !important;
}

/* 头像优化 */
.stChatMessage img {
    border: 2px solid rgba(255, 255, 255, 0.8) !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15) !important;
}
</style>
""", unsafe_allow_html=True)

# ===== 背景图 =====
set_background("水墨背景.png")
set_sidebar_background("装饰云彩.png")

# ===== 顶部 LOGO 和 Slogan（舒适布局） =====
dao_icon_base64 = image_to_base64("道icon.png")
if dao_icon_base64:
    st.markdown(f"""
    <div style="text-align:center; margin-bottom:4rem; display: flex; flex-direction: column; align-items: center; padding-top: 2rem;">
        <img src="data:image/png;base64,{dao_icon_base64}" alt="道"
             style="width:100px; height:100px; border-radius:50%; 
                    box-shadow: 0px 6px 20px rgba(0, 0, 0, 0.1); 
                    margin-bottom: 2rem; transition: transform 0.3s ease;
                    object-fit: cover; display: block;"
             onmouseover="this.style.transform='scale(1.05)'"
             onmouseout="this.style.transform='scale(1)'">
        <div style="display: flex; flex-direction: column; align-items: center; text-align: center;">
            <h1 style="font-family: 'Playfair Display', serif; font-size:2.8rem; font-weight:600; 
                       color:#1a202c; margin: 0 0 1.2rem 0; letter-spacing: -0.015em;
                       text-shadow: 0 2px 4px rgba(255,255,255,0.9); line-height: 1.1;">
                Dao AI
            </h1>
            <p class="subtitle" style="font-family: 'Noto Serif', serif; font-size:1.1rem; font-weight:400;
                                       color:#4a5568; margin: 0; letter-spacing: 0.01em;
                                       text-shadow: 0 1px 2px rgba(255,255,255,0.8); line-height: 1.5;
                                       max-width: 450px;">
                Chinese Wisdom · Enrich Your Mind & Soul
            </p>
        </div>
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

# ===== 左侧栏选择导师（修复点击功能） =====
with st.sidebar:
    st.markdown("""
        <h3 style="font-family: 'Inter', sans-serif; font-size:1.15rem; font-weight:600; 
                   color:#2d3748; margin-bottom: 1.5rem; letter-spacing: -0.01em;">
            Choose Your Sage
        </h3>
    """, unsafe_allow_html=True)
    
    # 初始化选中的导师
    if "selected_mentor" not in st.session_state:
        st.session_state.selected_mentor = mentor_names[0]
    
    # 为每个导师创建可点击的按钮和装饰卡片
    for mentor in mentor_names:
        is_selected = mentor == st.session_state.selected_mentor
        mentor_avatar = get_avatar_base64(mentor)
        
        # 创建两列：头像列和按钮列
        col1, col2 = st.columns([1, 2.5])
        
        with col1:
            # 显示头像
            if mentor_avatar:
                st.markdown(f"""
                <div style="text-align: center; margin-bottom: 0.5rem; margin-top: 0.3rem;">
                    <img src="{mentor_avatar}" 
                         style="width: 50px; height: 50px; border-radius: 50%; 
                                object-fit: cover; border: 2.5px solid {'#4a6fa5' if is_selected else 'rgba(255,255,255,0.8)'};
                                box-shadow: 0 3px 10px rgba(0,0,0,0.12);
                                transition: all 0.25s ease;">
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            # 创建可点击的按钮
            if st.button(
                mentor,
                key=f"sage_btn_{mentor}",
                use_container_width=True,
                type="primary" if is_selected else "secondary"
            ):
                if mentor != st.session_state.selected_mentor:
                    st.session_state.selected_mentor = mentor
                    st.session_state.agent = RAGAgent(persona=mentor)
                    st.session_state.chat_history = []
                    st.rerun()
        
        # 添加分隔线
        if mentor != mentor_names[-1]:
            st.markdown("<div style='margin: 0.8rem 0; height: 1px; background: rgba(0,0,0,0.06);'></div>", unsafe_allow_html=True)
    
    # 添加自定义CSS来美化按钮
    st.markdown("""
    <style>
    div[data-testid="stSidebar"] button[kind="primary"] {
        background: linear-gradient(135deg, #4a6fa5, #2d4a6b) !important;
        border: 1px solid #2d4a6b !important;
        color: white !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: all 0.25s ease !important;
    }
    
    div[data-testid="stSidebar"] button[kind="primary"]:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(74, 111, 165, 0.3) !important;
    }
    
    div[data-testid="stSidebar"] button[kind="secondary"] {
        background: rgba(255,255,255,0.8) !important;
        border: 1px solid rgba(226, 232, 240, 0.6) !important;
        color: #2d3748 !important;
        border-radius: 12px !important;
        font-weight: 500 !important;
        transition: all 0.25s ease !important;
    }
    
    div[data-testid="stSidebar"] button[kind="secondary"]:hover {
        background: rgba(255,255,255,0.95) !important;
        border-color: #4a6fa5 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(74, 111, 165, 0.15) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ===== 初始化 Agent =====
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "agent" not in st.session_state:
    st.session_state.agent = RAGAgent(persona=st.session_state.selected_mentor)

# ===== 获取导师头像（聊天气泡头像） =====
portrait_base64 = get_avatar_base64(st.session_state.selected_mentor)

# ===== 显示当前对话导师提示（细微优化版本） =====
st.markdown(f"""
<div style="text-align:center; margin:2rem 0 1.5rem;">
    <div style="font-family: 'Noto Serif', serif; font-size:1.1rem; font-weight:400; 
                color:#4a5568; opacity: 0.85; letter-spacing: 0.02em;
                text-shadow: 0 1px 2px rgba(255,255,255,0.9);">
        Seeking wisdom from {st.session_state.selected_mentor}
    </div>
</div>
""", unsafe_allow_html=True)

# ===== 显示聊天历史 =====
for msg in st.session_state.chat_history:
    with st.chat_message("user", avatar=get_user_avatar()):
        st.markdown(msg["question"])
    with st.chat_message("assistant", avatar=portrait_base64):
        st.markdown(msg["answer"])

# ===== 输入问题（细微优化） =====
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
    with st.spinner("Consulting ancient wisdom..."):
        try:
            question = st.session_state.chat_history[-1]["question"]
            answer = st.session_state.agent.ask(question)
            st.session_state.chat_history[-1]["answer"] = answer
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error in RAGAgent.ask: {str(e)}")
            st.session_state.chat_history[-1]["answer"] = f"I apologize, but I encountered an error while seeking wisdom: {e}"
            st.rerun()

# ===== 页脚（细微优化） =====
st.markdown("""
<div style="text-align:center; margin-top:4rem; padding-top: 2rem;">
    <p class="footer-text" style="font-family: 'Noto Serif', serif; font-weight:300; 
                                  color:#718096; font-size:0.95rem; letter-spacing: 0.03em;
                                  text-shadow: 0 1px 2px rgba(255,255,255,0.6);">
        道可道，非常道 · 名可名，非常名
    </p>
</div>
""", unsafe_allow_html=True)
