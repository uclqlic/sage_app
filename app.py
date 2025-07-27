import os
import json
import base64
import streamlit as st
from rag_agent import RAGAgent

# ===== 页面配置 =====
st.set_page_config(
    page_title="Dao AI - Ancient Wisdom for Modern Times",
    page_icon="🧘",
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

# ===== 世界级设计系统 =====
def apply_design_system():
    st.markdown("""
    <style>
    /* Design System - Typography & Colors */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@400;500;600;700&display=swap');
    
    :root {
        --primary-50: #f0f9ff;
        --primary-100: #e0f2fe;
        --primary-500: #0ea5e9;
        --primary-600: #0284c7;
        --primary-700: #0369a1;
        --primary-900: #0c4a6e;
        
        --neutral-50: #fafafa;
        --neutral-100: #f5f5f5;
        --neutral-200: #e5e5e5;
        --neutral-300: #d4d4d4;
        --neutral-400: #a3a3a3;
        --neutral-500: #737373;
        --neutral-600: #525252;
        --neutral-700: #404040;
        --neutral-800: #262626;
        --neutral-900: #171717;
        
        --spacing-xs: 0.25rem;
        --spacing-sm: 0.5rem;
        --spacing-md: 1rem;
        --spacing-lg: 1.5rem;
        --spacing-xl: 2rem;
        --spacing-2xl: 3rem;
        
        --radius-sm: 6px;
        --radius-md: 8px;
        --radius-lg: 12px;
        --radius-xl: 16px;
        --radius-2xl: 20px;
        
        --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
        --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1);
    }
    
    /* Global Reset & Base Styles */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        color: var(--neutral-800);
        line-height: 1.6;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Enhanced Sidebar Design */
    .stSidebar {
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(20px) saturate(180%) !important;
        border-right: 1px solid rgba(0, 0, 0, 0.06) !important;
        box-shadow: var(--shadow-lg) !important;
    }
    
    .stSidebar > div:first-child {
        padding: var(--spacing-xl) !important;
    }
    
    /* Main Content Area */
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: var(--spacing-xl);
        min-height: 100vh;
        display: flex;
        flex-direction: column;
    }
    
    /* Brand Header */
    .brand-section {
        text-align: center;
        margin-bottom: var(--spacing-2xl);
        position: relative;
    }
    
    .brand-logo {
        width: 96px;
        height: 96px;
        margin: 0 auto var(--spacing-lg);
        background: linear-gradient(135deg, var(--primary-500), var(--primary-700));
        border-radius: var(--radius-2xl);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.5rem;
        box-shadow: var(--shadow-xl);
        transition: transform 0.2s ease;
    }
    
    .brand-logo:hover {
        transform: translateY(-2px);
    }
    
    .brand-title {
        font-family: 'Playfair Display', serif;
        font-size: clamp(2.5rem, 5vw, 4rem);
        font-weight: 600;
        background: linear-gradient(135deg, var(--neutral-800), var(--neutral-600));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: var(--spacing-sm);
        letter-spacing: -0.02em;
    }
    
    .brand-subtitle {
        font-size: 1.125rem;
        color: var(--neutral-600);
        font-weight: 400;
        max-width: 400px;
        margin: 0 auto;
    }
    
    /* Sage Selection Cards */
    .sage-section-title {
        font-size: 1.125rem;
        font-weight: 600;
        color: var(--neutral-800);
        margin-bottom: var(--spacing-lg);
        display: flex;
        align-items: center;
        gap: var(--spacing-sm);
    }
    
    .sage-card {
        display: flex;
        align-items: center;
        padding: var(--spacing-md);
        margin-bottom: var(--spacing-md);
        border-radius: var(--radius-xl);
        cursor: pointer;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        border: 2px solid transparent;
        position: relative;
        overflow: hidden;
    }
    
    .sage-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, rgba(14, 165, 233, 0.05), rgba(59, 130, 246, 0.02));
        opacity: 0;
        transition: opacity 0.2s ease;
        z-index: -1;
    }
    
    .sage-card:hover::before {
        opacity: 1;
    }
    
    .sage-card:hover {
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
        border-color: var(--primary-200);
    }
    
    .sage-card.active {
        background: linear-gradient(135deg, var(--primary-50), rgba(14, 165, 233, 0.05));
        border-color: var(--primary-300);
        box-shadow: var(--shadow-lg);
    }
    
    .sage-card.active::before {
        opacity: 1;
    }
    
    .sage-avatar {
        width: 56px;
        height: 56px;
        border-radius: 50%;
        object-fit: cover;
        margin-right: var(--spacing-md);
        border: 3px solid rgba(255, 255, 255, 0.8);
        box-shadow: var(--shadow-md);
        transition: all 0.2s ease;
    }
    
    .sage-card.active .sage-avatar {
        border-color: var(--primary-300);
        box-shadow: 0 0 0 2px var(--primary-100);
    }
    
    .sage-info {
        flex: 1;
    }
    
    .sage-name {
        font-size: 1rem;
        font-weight: 600;
        color: var(--neutral-800);
        margin-bottom: var(--spacing-xs);
        line-height: 1.4;
    }
    
    .sage-description {
        font-size: 0.875rem;
        color: var(--neutral-500);
        line-height: 1.4;
    }
    
    .sage-card.active .sage-name {
        color: var(--primary-700);
    }
    
    .sage-status-indicator {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--primary-500);
        opacity: 0;
        transition: opacity 0.2s ease;
        margin-left: var(--spacing-sm);
    }
    
    .sage-card.active .sage-status-indicator {
        opacity: 1;
    }
    
    /* Chat Area */
    .chat-section {
        flex: 1;
        margin-top: var(--spacing-xl);
    }
    
    .current-sage-indicator {
        text-align: center;
        margin-bottom: var(--spacing-xl);
        padding: var(--spacing-md) var(--spacing-lg);
        background: rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(10px);
        border-radius: var(--radius-2xl);
        border: 1px solid rgba(255, 255, 255, 0.2);
        display: inline-block;
        margin-left: auto;
        margin-right: auto;
        box-shadow: var(--shadow-sm);
    }
    
    .current-sage-text {
        font-size: 0.9375rem;
        color: var(--neutral-600);
        font-weight: 500;
        margin: 0;
    }
    
    /* Chat Messages */
    .stChatMessage {
        background: transparent !important;
        padding: var(--spacing-lg) 0 !important;
    }
    
    /* Input Enhancement */
    .stChatInputContainer {
        background: rgba(255, 255, 255, 0.9) !important;
        border-radius: var(--radius-xl) !important;
        border: 2px solid rgba(14, 165, 233, 0.1) !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: var(--shadow-lg) !important;
        transition: all 0.2s ease !important;
    }
    
    .stChatInputContainer:focus-within {
        border-color: var(--primary-300) !important;
        box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.1), var(--shadow-xl) !important;
        transform: translateY(-1px) !important;
    }
    
    .stChatInput input {
        font-size: 1rem !important;
        color: var(--neutral-700) !important;
        font-weight: 400 !important;
    }
    
    .stChatInput input::placeholder {
        color: var(--neutral-400) !important;
        font-style: italic !important;
    }
    
    /* Footer */
    .footer-section {
        text-align: center;
        margin-top: var(--spacing-2xl);
        padding-top: var(--spacing-xl);
        border-top: 1px solid rgba(0, 0, 0, 0.06);
    }
    
    .footer-text {
        font-family: 'Playfair Display', serif;
        font-size: 0.9375rem;
        color: var(--neutral-500);
        font-weight: 400;
        font-style: italic;
        letter-spacing: 0.02em;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main-container {
            padding: var(--spacing-md);
        }
        
        .brand-title {
            font-size: 2.5rem;
        }
        
        .sage-card {
            padding: var(--spacing-sm);
        }
        
        .sage-avatar {
            width: 48px;
            height: 48px;
        }
    }
    
    /* Loading and States */
    .stSpinner {
        text-align: center;
        color: var(--primary-500);
    }
    
    /* Scrollbar Styling */
    ::-webkit-scrollbar {
        width: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--neutral-100);
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--neutral-300);
        border-radius: 3px;
        transition: background 0.2s ease;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--neutral-400);
    }
    
    /* Accessibility */
    .sage-card:focus {
        outline: 2px solid var(--primary-500);
        outline-offset: 2px;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .animate-in {
        animation: fadeIn 0.3s ease-out;
    }
    </style>
    """, unsafe_allow_html=True)

# ===== 设置背景 =====
def set_background(image_path):
    bg_base64 = image_to_base64(image_path)
    if bg_base64:
        st.markdown(f"""
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(248, 250, 252, 0.8), rgba(226, 232, 240, 0.6)), 
                              url("data:image/png;base64,{bg_base64}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """, unsafe_allow_html=True)

# ===== 应用设计系统 =====
apply_design_system()
set_background("水墨背景.png")

# ===== 加载人物数据 =====
@st.cache_data(show_spinner=False)
def load_personas():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(current_dir, "personas.json"), "r", encoding="utf-8") as f:
        return json.load(f)

personas = load_personas()
mentor_names = list(personas.keys())

# ===== 贤者描述映射 =====
sage_descriptions = {
    "孔子": "The Great Teacher • Wisdom & Ethics",
    "老子": "The Sage of Dao • Balance & Harmony", 
    "庄子": "The Dreamer • Freedom & Nature",
    "南怀瑾": "Modern Master • Tradition & Practice",
    "曾国藩": "The Strategist • Leadership & Self-cultivation"
}

# ===== 初始化状态 =====
if "selected_mentor" not in st.session_state:
    st.session_state.selected_mentor = mentor_names[0]
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "agent" not in st.session_state:
    st.session_state.agent = RAGAgent(persona=st.session_state.selected_mentor)

# ===== 左侧栏 - 世界级贤者选择器 =====
with st.sidebar:
    st.markdown("""
    <div class="sage-section-title">
        <span>🧘</span>
        <span>Choose Your Sage</span>
    </div>
    """, unsafe_allow_html=True)
    
    for mentor in mentor_names:
        mentor_avatar = get_avatar_base64(mentor)
        is_selected = mentor == st.session_state.selected_mentor
        description = sage_descriptions.get(mentor, "Ancient Philosopher")
        
        # 生成唯一的key来避免重复
        card_key = f"sage_card_{mentor}_{hash(mentor)}"
        
        # 头像HTML
        if mentor_avatar:
            avatar_html = f'<img src="{mentor_avatar}" class="sage-avatar" alt="{mentor}">'
        else:
            avatar_html = f'''
            <div class="sage-avatar" style="
                background: linear-gradient(135deg, #0ea5e9, #0284c7);
                display: flex; align-items: center; justify-content: center;
                color: white; font-weight: 600; font-size: 1.25rem;
            ">{mentor[0]}</div>
            '''
        
        # 创建可点击的卡片
        card_html = f"""
        <div class="sage-card {'active' if is_selected else ''}" 
             onclick="document.querySelector('[data-testid=\\"baseButton-secondary\\"][key=\\"{card_key}\\"]').click()"
             style="margin-bottom: 1rem;">
            {avatar_html}
            <div class="sage-info">
                <div class="sage-name">{mentor}</div>
                <div class="sage-description">{description}</div>
            </div>
            <div class="sage-status-indicator"></div>
        </div>
        """
        
        st.markdown(card_html, unsafe_allow_html=True)
        
        # 隐藏的按钮用于处理点击
        if st.button("", key=card_key, type="secondary", help=f"Select {mentor}"):
            if mentor != st.session_state.selected_mentor:
                st.session_state.selected_mentor = mentor
                st.session_state.agent = RAGAgent(persona=mentor)
                st.session_state.chat_history = []
                st.rerun()

# ===== 主内容区域 =====
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# 品牌标题
st.markdown("""
<div class="brand-section animate-in">
    <div class="brand-logo">🧘</div>
    <h1 class="brand-title">Dao AI</h1>
    <p class="brand-subtitle">Ancient Wisdom for Modern Times</p>
</div>
""", unsafe_allow_html=True)

# 当前对话指示器
st.markdown(f"""
<div style="text-align: center; margin-bottom: 2rem;">
    <div class="current-sage-indicator">
        <p class="current-sage-text">Seeking wisdom from {st.session_state.selected_mentor}</p>
    </div>
</div>
""", unsafe_allow_html=True)

# 聊天区域
st.markdown('<div class="chat-section">', unsafe_allow_html=True)

# 显示聊天历史
for msg in st.session_state.chat_history:
    with st.chat_message("user", avatar=get_user_avatar()):
        st.markdown(msg["question"])
    with st.chat_message("assistant", avatar=get_avatar_base64(st.session_state.selected_mentor)):
        st.markdown(msg["answer"])

# 输入框
user_question = st.chat_input("Share your thoughts and seek ancient wisdom...")

st.markdown('</div>', unsafe_allow_html=True)  # 结束聊天区域

# 页脚
st.markdown("""
<div class="footer-section">
    <p class="footer-text">道可道，非常道 · 名可名，非常名</p>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # 结束主容器

# ===== 处理用户输入 =====
if user_question:
    st.session_state.chat_history.append({"question": user_question, "answer": ""})
    st.rerun()

# ===== 生成答案 =====
if (
    st.session_state.chat_history and
    st.session_state.chat_history[-1]["answer"] == ""
):
    with st.spinner("🤔 The sage is contemplating your question..."):
        try:
            question = st.session_state.chat_history[-1]["question"]
            answer = st.session_state.agent.ask(question)
            st.session_state.chat_history[-1]["answer"] = answer
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.session_state.chat_history[-1]["answer"] = f"I apologize, but I encountered an error while seeking wisdom: {e}"
            st.rerun()
